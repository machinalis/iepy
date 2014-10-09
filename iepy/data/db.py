"""
IEPY DB Abstraction level.

The goal of this module is to provide some thin abstraction between
the chosen database engine and ORM and the IEPY core and tools.
"""

from collections import namedtuple
try:
    from functools import lru_cache
except:
    from functools32 import lru_cache

import iepy
iepy.setup()

from iepy.data.models import IEDocument, TextSegment, Entity, EntityKind, Relation
from iepy.preprocess.pipeline import PreProcessSteps


IEPYDBConnector = namedtuple('IEPYDBConnector', 'segments documents')

# Number of entities that will be cached on get_entity function.
ENTITY_CACHE_SIZE = 20  # reasonable compromise


class DocumentManager(object):
    """Wrapper to the db-access, so it's not that impossible to switch
    from mongodb to something else if desired.
    """

    ### Basic administration and pre-process

    def create_document(self, identifier, text, metadata=None):
        """Creates a new Document with text ready to be inserted on the
        information extraction pipeline (ie, ready to be tokenized, POS Tagged,
        etc).

        Identifier must be a unique value that will be used for distinguishing
        one document from another. If no title is given, will be inferred from
        the identifier.
        Metadata is a dictionary where you can put whatever you want to persist
        with your document. IEPY will do nothing with it except ensuring that
        such information will be preserved.
        """
        if metadata is None:
            metadata = {}
        doc = IEDocument(human_identifier=identifier, text=text, metadata=metadata)
        doc.save()
        return doc

    def __iter__(self):
        return iter(IEDocument.objects.all())

    def get_raw_documents(self):
        """returns an interator of documents that lack the text field, or it's
        empty.
        """
        return IEDocument.objects.filter(text='')

    def get_documents_lacking_preprocess(self, step):
        """Returns an iterator of documents that shall be processed on the given
        step."""
        if step in PreProcessSteps:
            flag_field_name = "%s_done_at" % step.name
            query = {"%s__isnull" % flag_field_name: True}
            return IEDocument.objects.filter(**query).order_by('id')
        return IEDocument.objects.none()


class TextSegmentManager(object):

    @classmethod
    def get_segment(cls, document_identifier, offset):
        # FIXME: this is still mongo storage dependent
        d = IEDocument.objects.get(human_identifier=document_identifier)
        return TextSegment.objects.get(document=d, offset=offset)


class EntityManager(object):

    @classmethod
    def ensure_kinds(cls, kind_names):
        for kn in kind_names:
            EntityKind.objects.get_or_create(name=kn)

    @classmethod
    @lru_cache(maxsize=ENTITY_CACHE_SIZE)
    def get_entity(cls, kind, literal):
        kw = {'key': literal}
        if isinstance(kind, int):
            kw['kind_id'] = kind
        else:
            kw['kind__name'] = kind
        return Entity.objects.get(**kw)


class RelationManager(object):
    @classmethod
    def get_relation(cls, pk):
        return Relation.objects.get(pk=pk)

    @classmethod
    def dict_by_id(cls):
        return dict((r.pk, r) for r in Relation.objects.all())


class CandidateEvidenceManager(object):

    @classmethod
    def hydrate(cls, ev):
        ev.evidence = ev.segment.hydrate()
        ev.right_entity_occurrence.hydrate_for_segment(ev.segment)
        ev.left_entity_occurrence.hydrate_for_segment(ev.segment)
        return ev

    @classmethod
    def candidates_for_relation(cls, relation):
        # Wraps the actual database lookup of evidence, hydrating them so
        # in theory, no extra db access shall be done
        evidences = []
        hydrate = cls.hydrate
        for segment in relation._matching_text_segments():
            evidences.extend(
                [hydrate(e) for e in segment.get_evidences_for_relation(relation)]
            )
        return evidences


