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

from iepy.data.models import IEDocument, TextSegment, Entity, EntityKind
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

    def segments_with_both_entities(self, entity_a, entity_b):
        key_a, key_b = entity_a.key, entity_b.key
        return TextSegment.objects(entities__key=key_a)(entities__key=key_b)

    def segments_with_both_kinds(self, kind_a, kind_b):
        if kind_a != kind_b:
            return list(TextSegment.objects(entities__kind=kind_a)(entities__kind=kind_b))
        else:
            # Need a different query here, we need to check that the type
            # appears twice
            db = get_db()
            pipeline = [
                {'$match': {"entities.kind": kind_a}},
                {'$unwind': "$entities"},
                {'$group': {
                    '_id': {'_id': "$_id", 'k': "$entities.kind"},
                    'count': {'$sum': 1}
                }},
                {'$match': {'_id.k': kind_a, 'count': {'$gte': 2}}},
                {'$project': {'_id': 0, 'id': "$_id._id"}},
            ]

            objects = db.text_segment.aggregate(pipeline)
            segments = list(TextSegment.objects.in_bulk([c['id'] for c in objects[u'result']]).values())
            return segments


class EntityManager(object):

    @classmethod
    def ensure_kinds(cls, kind_names):
        for kn in kind_names:
            EntityKind.objects.get_or_create(name=kn)



@lru_cache(maxsize=ENTITY_CACHE_SIZE)
def get_entity(kind, literal):
    return Entity.objects.get(kind=kind, key=literal)


def get_segment(document_identifier, offset):
    d = IEDocument.objects.get(human_identifier=document_identifier)
    return TextSegment.objects.get(document=d, offset=offset)
