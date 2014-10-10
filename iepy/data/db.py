"""
IEPY DB Abstraction level.

The goal of this module is to provide some thin abstraction between
the chosen database engine and ORM and the IEPY core and tools.
"""

from collections import namedtuple
from functools import lru_cache
import logging

import iepy
iepy.setup()

from iepy.data.models import (
    IEDocument, TextSegment, Entity, EntityKind, Relation, EvidenceLabel)
from iepy.preprocess.pipeline import PreProcessSteps


IEPYDBConnector = namedtuple('IEPYDBConnector', 'segments documents')

# Number of entities that will be cached on get_entity function.
ENTITY_CACHE_SIZE = 20  # reasonable compromise

logger = logging.getLogger(__name__)


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

    @classmethod
    def labeled_candidates_for_relation(cls, relation, conflict_solver=None):
        logger.info("Loading candidate evidence from database...")
        candidates = {e: None for e in cls.candidates_for_relation()}

        labels = EvidenceLabel.object.filter(evidence_candidate__relation=relation,
                                             label__in=[EvidenceLabel.NORELATION,
                                                        EvidenceLabel.YESRELATION,
                                                        EvidenceLabel.NONSENSE])
        for e in candidates:
            # This is CRYING for a preformance refactor. Will make a DB-query per
            # evidence, when could do only one query for all and handle it on memory.
            # If runs slows, here there's place for improvement
            answers = labels.filter(evidence_candidate=e)
            if not answers:
                continue
            if len(answers) == 1:
                lbl = answers[0].label
            elif len(set([a.label for a in answers])) == 1:
                # several answers, all the same. Just pick the first one
                lbl = answers[0].label
            elif conflict_solver:
                preferred = conflict_solver(answers)
                if preferred is None:
                    # unsolvable conflict
                    continue
                lbl = preferred.label
            else:
                continue
            # Ok, we have a choosen answer. Lets see if it's informative
            if lbl.label == EvidenceLabel.NONSENSE:
                # too bad, not informative
                continue
            elif lbl.label == EvidenceLabel.NORELATION:
                candidates[e] = False
            elif lbl.label == EvidenceLabel.YESRELATION:
                candidates[e] = True
        return candidates

    @classmethod
    def conflict_resolution_by_judge_name(cls, judges_order):
        # Only consider answers for the given judges, prefering those of the judge listed
        # first. Returns None if not found.
        def solver(ev_labels):
            # expects to be called only when len(ev_labels) > 1
            ev_labels = [el for el in ev_labels if el.judge in judges_order]
            if ev_labels:
                ev_labels.sort(key=lambda el: judges_order.index(el.judge))
                return ev_labels[0]
            return None
        return solver

    @classmethod
    def conflict_resolution_newest_wins(cls):
        def solver(ev_labels):
            # expects to be called only when len(ev_labels) > 1
            return sorted(ev_labels[:], key=lambda el: el.modification_date)[0]
        return solver
