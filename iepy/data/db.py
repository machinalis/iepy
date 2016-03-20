"""
IEPY DB Abstraction level.

The goal of this module is to provide some thin abstraction between
the chosen database engine and ORM and the IEPY core and tools.
"""

from collections import defaultdict, namedtuple
from functools import lru_cache
from random import shuffle
import logging

import iepy
iepy.setup()

from iepy.data.models import (
    IEDocument, IEDocumentMetadata,
    TextSegment, Relation,
    Entity, EntityKind, EntityOccurrence,
    EvidenceLabel, EvidenceCandidate
)

from iepy.preprocess import segmenter
from iepy.preprocess.pipeline import PreProcessSteps


IEPYDBConnector = namedtuple('IEPYDBConnector', 'segments documents')

# Number of entities that will be cached on get_entity function.
ENTITY_CACHE_SIZE = 20  # reasonable compromise

logger = logging.getLogger(__name__)


class DocumentManager(object):
    """Wrapper to the db-access, so it's not that impossible to switch
    from current ORM to something else if desired.
    """

    ### Basic administration and pre-process
    def __init__(self, base_queryset=None):
        self.base_queryset = base_queryset

    def create_document(self, identifier, text, metadata=None, update_mode=False):
        """Creates a new Document with text ready to be inserted on the
        information extraction pipeline (ie, ready to be tokenized, POS Tagged,
        etc).

        Identifier must be a unique value that will be used for distinguishing
        one document from another.
        Metadata is a dictionary where you can put whatever you want to persist
        with your document. IEPY will do nothing with it except ensuring that
        such information will be preserved.

        With update_mode enabled, then if there's an existent document with the
        provided identifier, it's updated (be warn that if some preprocess
        result exist will be preserved untouched, delegating the responsability
        of deciding what to do to the caller of this method).
        """
        if metadata is None:
            metadata = {}

        filter_query = IEDocument.objects.filter(human_identifier=identifier)
        if not filter_query.exists():
            mtd_obj = IEDocumentMetadata.objects.create(items=metadata)
            doc = IEDocument.objects.create(human_identifier=identifier, text=text,
                                            metadata=mtd_obj)
        else:
            doc = filter_query.get()
        if update_mode:
            doc.text = text
            doc.metadata.items = metadata
            doc.metadata.save()
            doc.save()

        return doc

    def _docs(self):
        if self.base_queryset:
            docs = self.base_queryset
        else:
            docs = IEDocument.objects.all()
        return docs

    def __iter__(self):
        return iter(self._docs())

    def get_raw_documents(self):
        """returns an interator of documents that lack the text field, or it's
        empty.
        """
        return self._docs().filter(text='')

    def get_documents_lacking_preprocess(self, step_or_steps):
        """Returns an iterator of documents that shall be processed on the given
        step."""
        from django.db.models import Q
        if not isinstance(step_or_steps, (list, tuple)):
            steps = [step_or_steps]
        else:
            steps = step_or_steps
        query = None
        for step in steps:
            if step in PreProcessSteps:
                flag_field_name = "%s_done_at" % step.name
                q = Q(**{"%s__isnull" % flag_field_name: True})
                if query is None:
                    query = q
                else:
                    query = query | q
        if query is not None:
            return self._docs().filter(query).order_by('id')
        else:
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


class EntityOccurrenceManager:

    @classmethod
    def create_with_entity(cls, kind, document, offset, offset_end):
        entity, _ = Entity.objects.get_or_create(
            key="{} {} {} {}".format(
                document.human_identifier,
                kind, offset, offset_end
            ),
            kind=kind
        )
        entity_occurrence = EntityOccurrence(
            entity=entity,
            document=document,
            offset=offset,
            offset_end=offset_end,
            alias=" ".join(document.tokens[offset:offset_end]),
        )
        entity_occurrence.save()
        segmenter_runner = segmenter.SyntacticSegmenterRunner(override=True)
        segmenter_runner(document)


class RelationManager(object):
    @classmethod
    def get_relation(cls, pk):
        return Relation.objects.get(pk=pk)

    @classmethod
    def dict_by_id(cls):
        return dict((r.pk, r) for r in Relation.objects.all())


class CandidateEvidenceManager(object):

    @classmethod
    def hydrate(cls, ev, document=None):
        ev.evidence = ev.segment.hydrate(document)
        ev.right_entity_occurrence.hydrate_for_segment(ev.segment)
        ev.left_entity_occurrence.hydrate_for_segment(ev.segment)
        # contains a duplicate of left and right eo. Not big deal
        ev.all_eos = ev.segment.get_entity_occurrences()
        return ev

    @classmethod
    def candidates_for_relation(cls, relation, construct_missing_candidates=True,
                                seg_limit=-1, shuffle_segs=False):
        # Wraps the actual database lookup of evidence, hydrating them so
        # in theory, no extra db access shall be done
        # The idea here is simple, but with some tricks for improving performance
        logger.info("Loading candidate evidence from database...")
        hydrate = cls.hydrate
        segments_per_document = defaultdict(list)

        raw_segments = {}
        segments = relation._matching_text_segments()
        if shuffle_segs:
            segments = list(segments)
            shuffle(segments)

        for i, s in enumerate(segments):
            if seg_limit >= 0 and i >= seg_limit:
                break
            raw_segments[s.id] = s

        for s in raw_segments.values():
            segments_per_document[s.document_id].append(s)
        doc_ids = segments_per_document.keys()
        existent_ec = EvidenceCandidate.objects.filter(
            left_entity_occurrence__entity__kind=relation.left_entity_kind,
            right_entity_occurrence__entity__kind=relation.right_entity_kind,
            segment__in=raw_segments.keys()
        ).select_related(
            'left_entity_occurrence', 'right_entity_occurrence', 'segment'
        )
        existent_ec_per_segment = defaultdict(list)
        for ec in existent_ec:
            existent_ec_per_segment[ec.segment_id].append(ec)

        _doc_ids = list(doc_ids)
        while _doc_ids:
            _id = _doc_ids.pop()
            document = IEDocument.objects.get(id=_id)
            for segment in segments_per_document[document.id]:
                _existent = existent_ec_per_segment[segment.pk]
                if construct_missing_candidates:
                    seg_ecs = segment.get_evidences_for_relation(relation, _existent)
                else:
                    seg_ecs = _existent

                for evidence in seg_ecs:
                    yield hydrate(evidence, document)

    @classmethod
    def value_labeled_candidates_count_for_relation(cls, relation):
        """Returns the count of labels for the given relation that provide actual
        information/value: YES or NO"""
        labels = EvidenceLabel.objects.filter(
            relation=relation,
            label__in=[EvidenceLabel.NORELATION, EvidenceLabel.YESRELATION],
            labeled_by_machine=False
        )
        return labels.count()

    @classmethod
    def labels_for(cls, relation, evidences, conflict_solver=None):
        """Returns a dict with the form evidence->[True|False|None]"""
        # Given a relation and a sequence of candidate-evidences, compute its
        # labels
        candidates = {e: None for e in evidences}

        logger.info("Getting labels from DB")
        labels = EvidenceLabel.objects.filter(
            relation=relation,
            label__in=[EvidenceLabel.NORELATION, EvidenceLabel.YESRELATION,
                       EvidenceLabel.NONSENSE],
            labeled_by_machine=False
        )
        logger.info("Sorting labels them by evidence")
        labels_per_ev = defaultdict(list)
        for l in labels:
            labels_per_ev[l.evidence_candidate].append(l)

        logger.info("Labels conflict solving")
        for e in candidates:
            answers = labels_per_ev[e]
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
            if lbl == EvidenceLabel.NONSENSE:
                # too bad, not informative
                continue
            elif lbl == EvidenceLabel.NORELATION:
                candidates[e] = False
            elif lbl == EvidenceLabel.YESRELATION:
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
    def conflict_resolution_newest_wins(cls, ev_labels):
        # expects to be called only when len(ev_labels) > 1
        return sorted(ev_labels[:], key=lambda el: el.modification_date, reverse=True)[0]
