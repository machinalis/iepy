# This module is the nexus/connection between the UI definitions (django models)
# and the IEPY models. Modifications of this file should be done with the
# awareness of this dual-impact.
from datetime import datetime
import itertools
import logging
from operator import attrgetter
from collections import namedtuple

from django.db import models

from iepy.utils import unzip
from corpus.fields import ListField
import jsonfield

CHAR_MAX_LENGHT = 256

logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'corpus'  # Name of the django app.


class EntityKind(BaseModel):
    # There's a fixture declaring an initial set of Entity Kinds, containing
    # PERSON, LOCATION, AND ORGANIZATION
    name = models.CharField(max_length=CHAR_MAX_LENGHT, unique=True)

    class Meta(BaseModel.Meta):
        ordering = ['name']

    def __str__(self):
        return self.name


class Entity(BaseModel):
    # the "key" IS the "canonical-form". Alieses are stored on
    # Entity Occurrences
    key = models.CharField(max_length=CHAR_MAX_LENGHT)
    kind = models.ForeignKey(EntityKind)

    class Meta(BaseModel.Meta):
        ordering = ['kind', 'key']
        unique_together = (('key', 'kind'), )

    def __str__(self):
        return '%s (%s)' % (self.key, self.kind.name)


class IEDocument(BaseModel):
    human_identifier = models.CharField(max_length=CHAR_MAX_LENGHT,
                                        unique=True)
    title = models.CharField(max_length=CHAR_MAX_LENGHT)  # TODO: remove
    url = models.URLField()  # TODO: remove
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    # The following 3 lists have 1 item per token
    tokens = ListField()  # strings
    offsets_to_text = ListField()  # ints, character offset for tokens
    postags = ListField()  # strings

    sentences = ListField()  # ints, it's a list of token-offsets

    # Reversed fields:
    # entity_occurrences = Reversed ForeignKey of EntityOccurrence
    # segments = Reversed ForeignKey of TextSegment

    # Metadata annotations that're computed while traveling the pre-process pipeline
    tokenization_done_at = models.DateTimeField(null=True, blank=True)
    sentencer_done_at = models.DateTimeField(null=True, blank=True)
    tagging_done_at = models.DateTimeField(null=True, blank=True)
    ner_done_at = models.DateTimeField(null=True, blank=True)
    segmentation_done_at = models.DateTimeField(null=True, blank=True)

    # anything else you want to store in here that can be useful
    metadata = jsonfield.JSONField(blank=True)

    class Meta(BaseModel.Meta):
        ordering = ['id', ]

    def __str__(self):
        return '<IEDocument {0}>'.format(self.human_identifier)

    def get_sentences(self):
        """Iterator over the sentences, each sentence being a list of tokens.
        """
        tokens = self.tokens
        sentences = self.sentences
        start = 0
        for i, end in enumerate(sentences[1:]):
            yield tokens[start:end]
            start = end

    def get_entity_occurrences(self):
        """Returns an iterable of EntityOccurrences, sorted by offset"""
        return self.entity_occurrences.all().order_by('offset')

    def get_text_segments(self):
        """Returns the iterable of TextSegments, sorted by offset"""
        return self.segments.all().order_by('offset')

    ### Methods used for preprocess ###

    def was_preprocess_step_done(self, step):
        return getattr(self, '%s_done_at' % step.name) is not None

    def set_tokenization_result(self, value):
        """Sets the value to the correspondent storage format"""
        if not isinstance(value, list):
            raise ValueError("Tokenization expected result should be a list "
                             "of tuples (token-offset on text (int), token-string).")
        tkn_offsets, tokens = unzip(value, 2)
        self.tokens = list(tokens)
        self.offsets_to_text = list(tkn_offsets)
        self.tokenization_done_at = datetime.now()
        return self

    def set_sentencer_result(self, value):
        if not isinstance(value, list):
            raise ValueError("Sentencer expected result should be a list.")
        if not all(isinstance(x, int) for x in value):
            raise ValueError('Sentencer result shall only contain ints: %r' % value)
        if sorted(value) != value:
            raise ValueError('Sentencer result shall be ordered.')
        if len(set(value)) < len(value):
            raise ValueError(
                'Sentencer result shall not contain duplicates.')
        if value[0] != 0:
            raise ValueError(
                'Sentencer result must start with 0. Actual=%r' % value[0])
        if value[-1] != len(self.tokens):
            raise ValueError(
                'Sentencer result must end with token count=%d. Actual=%r' % (
                    len(self.tokens), value[-1]))
        self.sentences = value
        self.sentencer_done_at = datetime.now()
        return self

    def set_tagging_result(self, value):
        if len(value) != len(self.tokens):
            raise ValueError(
                'Tagging result must have same cardinality than tokens')
        self.postags = value
        self.tagging_done_at = datetime.now()
        return self

    def set_ner_result(self, value):
        for found_entity in value:
            key, kind_name, alias, offset, offset_end = found_entity
            kind, _ = EntityKind.objects.get_or_create(name=kind_name)
            entity, created = Entity.objects.get_or_create(
                key=key,
                kind=kind)
            if len(alias) > CHAR_MAX_LENGHT:
                alias_ = alias[:CHAR_MAX_LENGHT]
                print('Alias "%s" reduced to "%s"' % (alias, alias_))
                alias = alias_
            EntityOccurrence.objects.get_or_create(
                document=self,
                entity=entity,
                offset=offset,
                offset_end=offset_end,
                alias=alias
            )
        self.ner_done_at = datetime.now()
        return self

    def set_segmentation_result(self, value, increment=True, override=False):
        if override:
            self.segments.all().delete()
            logger.info('Previous segments removed')
        get_offsets = attrgetter('offset', 'offset_end')
        value = sorted(value, key=get_offsets)
        logger.info('About to set %s segments for current doc', len(value))
        doc_ent_occurrences = list(self.entity_occurrences.all())
        currents = set(self.segments.all().values_list('offset', 'offset_end'))
        new_segs = []
        for i, raw_segment in enumerate(value):
            if (raw_segment.offset, raw_segment.offset_end) in currents:
                continue
            _segm = TextSegment(
                document=self, offset=raw_segment.offset,
                offset_end=raw_segment.offset_end)
            new_segs.append((_segm, raw_segment))
        if new_segs:
            TextSegment.objects.bulk_create(list(zip(*new_segs))[0])
            logger.info('New %s segments created', len(new_segs))
        # And now, taking care of setting Entity Occurrences

        doc_segments = dict((get_offsets(s), s) for s in self.segments.all())
        for _segm, raw_segment in new_segs:
            segm = doc_segments[get_offsets(_segm)]
            if raw_segment.entity_occurrences is None:
                # Entity Ocurrences not provided, need to compute them
                segm.entity_occurrences = [
                    eo for eo in doc_ent_occurrences
                    if eo.offset >= segm.offset
                    and eo.offset_end <= segm.offset_end
                ]
            else:
                segm.entity_occurrences = raw_segment.entity_occurrences

        self.segmentation_done_at = datetime.now()
        return self


class EntityOccurrence(BaseModel):
    """Models the occurrence of a particular Entity on a Document"""
    entity = models.ForeignKey('Entity')
    document = models.ForeignKey('IEDocument', related_name='entity_occurrences')
    segments = models.ManyToManyField('TextSegment', related_name='entity_occurrences')

    # Offset in tokens wrt to document
    offset = models.IntegerField()  # offset of the 1st token included on the occurrence
    offset_end = models.IntegerField()  # offset of the 1st token NOT included

    # Hydrated fields: same than "offsets", but wrt segment
    # segment_offset = IntegerField
    # segment_offset_end = IntegerField

    # Text of the occurrence, so if it's different than canonical_form, it's easy to see
    alias = models.CharField(max_length=CHAR_MAX_LENGHT)

    class Meta(BaseModel.Meta):
        ordering = ['document', 'offset', 'offset_end']
        unique_together = ['entity', 'document', 'offset', 'offset_end']

    def __str__(self):
        return '{0} ({1}, {2})'.format(self.entity.key, self.offset, self.offset_end)

    def hydrate_for_segment(self, segment):
        # creates some on-memory attributes with respect to the segment
        self.segment_offset = self.offset - segment.offset
        self.segment_offset_end = self.offset_end - segment.offset
        return self


class TextSegment(BaseModel):
    document = models.ForeignKey('IEDocument', related_name='segments', db_index=True)

    # Offset in tokens wrt to document
    #     They represent:
    #      - offset: index of the first token included on the segment
    #      - offset_end: index of the first token NOT included on the segment
    offset = models.IntegerField(db_index=True)
    offset_end = models.IntegerField(db_index=True)

    # Reversed fields:
    # entity_occurrences = Reversed ManyToManyField of EntityOccurrence

    class Meta(BaseModel.Meta):
        ordering = ['document', 'offset', 'offset_end']
        unique_together = ['document', 'offset', 'offset_end']

    def __str__(self):
        # return u'{0}'.format(' '.join(self.tokens))  # TODO: no tokens
        return u'({0} {1})'.format(self.offset, self.offset_end)

    def hydrate(self):
        # Using the segment offsets, and the data on document itself, constructs
        # on-memory attributes for the segment
        if getattr(self, '_hydrated', False):
            return self
        doc = self.document
        self.tokens = doc.tokens[self.offset: self.offset_end]
        self.offsets_to_text = doc.offsets_to_text[self.offset: self.offset_end]
        self.postags = doc.postags[self.offset: self.offset_end]
        if self.offsets_to_text:
            # grab the text except the last token
            self.text = doc.text[self.offsets_to_text[0]:
                                 doc.offsets_to_text[self.offset_end - 1]]
            # and now append the "pure" last token.
            self.text += self.tokens[-1]
        else:
            self.text = ""
        self.sentences = [i - self.offset for i in doc.sentences
                          if i >= self.offset and i < self.offset_end]
        self._hydrated = True
        return self

    def get_entity_occurrences(self):
        """Returns an iterable of EntityOccurrences, sorted by offset"""
        return map(lambda eo: eo.hydrate_for_segment(self),
                   self.entity_occurrences.all().order_by('offset')
                   )

    def get_evidences_for_relation(self, relation):
        # Gets or creates Labeled Evidences (when creating, label is empty)
        lkind = relation.left_entity_kind
        rkind = relation.right_entity_kind
        for l_eo, r_eo in self.kind_occurrence_pairs(lkind, rkind):
            obj, created = EvidenceCandidate.objects.get_or_create(
                left_entity_occurrence=l_eo,
                right_entity_occurrence=r_eo,
                relation=relation,
                segment=self,
            )
            yield obj

    def entity_occurrence_pairs(self, e1, e2):
        eos = list(self.get_entity_occurrences())
        left = [eo for eo in eos if eo.entity == e1]
        right = [eo for eo in eos if eo.entity == e2]
        return [(l, r) for l, r in itertools.product(left, right) if l != r]

    def kind_occurrence_pairs(self, lkind, rkind):
        eos = list(self.get_entity_occurrences())
        left = [o for o in eos if o.entity.kind == lkind]
        right = [o for o in eos if o.entity.kind == rkind]
        return [(l, r) for l, r in itertools.product(left, right) if l != r]

    def get_enriched_tokens(self):
        # TODO: implement real method
        eos = list(self.get_entity_occurrences())
        RichToken = namedtuple("RichToken", "token pos eo_ids eo_kinds")
        for tkn_offset, (tkn, postag) in enumerate(zip(self.tokens, self.postags)):
            tkn_eos = [eo for eo in eos
                       if eo.segment_offset <= tkn_offset < eo.segment_offset_end]
            yield RichToken(
                token=tkn,
                pos=postag,
                eo_ids=[eo.id for eo in tkn_eos],
                eo_kinds=[eo.entity.kind for eo in tkn_eos]
            )

    @classmethod
    def filter_by_entity_occurrence_kind_pair(cls, kind_a, kind_b):
        """Returns a queryset of TextSegments having at least one Entity
        Occurrence of the left entity kind, and at least one Entity Occurrence
        of the right entity kind. If left and rigth kinds are the same, at least
        two occurrences expected."""
        # This may be implemented as a Manager method, but for simplicity, will
        # be put in here as a classmethod.
        matching_segms = TextSegment.objects.filter(
            entity_occurrences__entity__kind=kind_a).distinct()
        if kind_a == kind_b:
            # BECAREFUL!!! There is a very subtle detail in here. The Django ORM,
            # after doing the first filter (before entering this if-branch) gave us
            # <TextSegments> whose "entity_occurrences" are not all of them, but only
            # those that match the criteria expressed above. Because of that, is that
            # when annotating Count of such thing, we trust is counting EOccurrences of
            # the kind we are interested in, and not the others.
            matching_segms = matching_segms.annotate(
                kind_count=models.Count('entity_occurrences__entity__kind')).filter(
                    kind_count__gte=2
                )
        else:
            matching_segms = matching_segms.filter(
                entity_occurrences__entity__kind=kind_b,
            ).distinct()
        return matching_segms


class Relation(BaseModel):
    name = models.CharField(max_length=CHAR_MAX_LENGHT)
    left_entity_kind = models.ForeignKey('EntityKind', related_name='left_relations')
    right_entity_kind = models.ForeignKey('EntityKind', related_name='right_relations')

    # Reversed fields:
    # evidence_relations = Reversed ForeignKey of EvidenceCandidate

    class Meta(BaseModel.Meta):
        ordering = ['name', 'left_entity_kind', 'right_entity_kind']
        unique_together = ['name', 'left_entity_kind', 'right_entity_kind']

    def __str__(self):
        return '{}({}, {})'.format(self.name, self.left_entity_kind,
                                   self.right_entity_kind)

    def save(self, *args, **kwargs):
        if self.pk:
            # Object already exists, this is a modification
            original_obj = Relation.objects.get(pk=self.pk)
            for fname in ['left_entity_kind', 'right_entity_kind']:
                if getattr(original_obj, fname) != getattr(self, fname):
                    raise ValueError("Relation kinds can't be modified after creation")
        return super(Relation, self).save(*args, **kwargs)

    def _matching_text_segments(self):
        return TextSegment.filter_by_entity_occurrence_kind_pair(
            self.right_entity_kind, self.left_entity_kind)

    def labeled_neighbor(self, obj, judge, back=False):
        """Returns the id of the "closest" labeled object to the one provided.
        Notes:
            - By "closest", it's mean the distance of the id numbers.
            - Works both for TextSegment and for IEDocument
            - If back is True, it's picked the previous item, otherwise, the next one.
            - It's assumed that the obj provided HAS labeled evidence already. If not,
              it's not possible to determine what is next. In such case, the id of the
              last labeled object will be returned.

            - If asking "next" and obj is currently the last, his id will be returned.
            - If asking "prev" and obj is currently the first, his id will be returned.
        """
        if isinstance(obj, TextSegment):
            segments = self._matching_text_segments()
            segments = segments.filter(evidence_relations__relation=self)
            judge_labels = EvidenceLabel.objects.filter(
                judge=judge,
                label__isnull=False,
                evidence_candidate__segment__in=segments,
            )
            candidates_with_label = judge_labels.values_list("evidence_candidate__segment", flat=True)
            segments = segments.filter(id__in=candidates_with_label).distinct()
            ids = list(segments.values_list('id', flat=True).order_by('id'))
        elif isinstance(obj, IEDocument):
            judge_labels = EvidenceLabel.objects.filter(
                judge=judge,
                label__isnull=False,
                evidence_candidate__relation=self,
            )
            ids = sorted(set(judge_labels.values_list(
                'evidence_candidate__segment__document_id', flat=True)
            ))
        else:
            ids = []
        if not ids:
            return None
        try:
            base_idx = ids.index(obj.id)
        except ValueError:
            # the base-object provided is not listed... Returning the base-object
            # Returning last in list
            return ids[-1]
        else:
            if back:
                if base_idx == 0:
                    # there is no previous one. Returning same.
                    return obj.id
                else:
                    return ids[base_idx - 1]
            else:
                if base_idx == len(ids) - 1:
                    # there is no next one. Returning same.
                    return obj.id
                else:
                    return ids[base_idx + 1]

    def get_next_segment_to_label(self, judge):
        # We'll pick first those Segments having already created questions with empty
        # answer (label=None). After finishing those, we'll look for
        # Segments never considered (ie, that doest have any question created).
        # Finally, those with answers in place, but with some answers "ASK-ME-LATER"
        segments = self._matching_text_segments().order_by('id')
        never_considered_segm = segments.exclude(evidence_relations__relation=self)

        evidences = EvidenceCandidate.objects.filter(
            relation=self
        ).order_by('segment_id')
        never_considered_ev = evidences.filter(labels__isnull=True)

        existent_labels = EvidenceLabel.objects.filter(
            evidence_candidate__in=evidences).order_by('evidence_candidate__segment_id')
        none_labels = existent_labels.filter(label__isnull=True)
        own_none_labels = none_labels.filter(judge=judge)

        # requires re answer if there's no Good answer at all (not just for this judge)
        NOT_NEED_RELABEL = [k for k, name in EvidenceLabel.LABEL_CHOICES
                            if k not in EvidenceLabel.NEED_RELABEL]
        to_re_answer = evidences.exclude(labels__label__in=NOT_NEED_RELABEL)

        for qset in [own_none_labels, never_considered_ev, never_considered_segm,
                     to_re_answer, none_labels]:
            try:
                obj = qset[0]
            except IndexError:
                pass
            else:
                if isinstance(obj, TextSegment):
                    return obj
                elif isinstance(obj, EvidenceCandidate):
                    return obj.segment
                elif isinstance(obj, EvidenceLabel):
                    return obj.evidence_candidate.segment
                else:
                    raise ValueError
        return None

    def get_next_document_to_label(self, judge):
        next_segment = self.get_next_segment_to_label(judge)
        if next_segment is None:
            return None
        else:
            return next_segment.document


class EvidenceCandidate(BaseModel):
    left_entity_occurrence = models.ForeignKey(
        'EntityOccurrence',
        related_name='left_evidence_relations'
    )
    right_entity_occurrence = models.ForeignKey(
        'EntityOccurrence',
        related_name='right_evidence_relations'
    )
    relation = models.ForeignKey('Relation', related_name='evidence_relations')
    segment = models.ForeignKey('TextSegment', related_name='evidence_relations')

    class Meta(BaseModel.Meta):
        ordering = [
            'segment_id', 'relation_id',
            'left_entity_occurrence', 'right_entity_occurrence',
        ]
        unique_together = [
            'left_entity_occurrence', 'right_entity_occurrence',
            'relation', 'segment'
        ]

    def __str__(self):
        s = "Candidate for the relation '{}({}, {})' in '{}'"
        return s.format(
            self.relation.name,
            self.left_entity_occurrence.alias,
            self.right_entity_occurrence.alias,
            self.segment
        )

    @property
    def fact(self):
        return (
            self.right_entity_occurrence.entity,
            self.relation, self.left_entity_occurrence.entity
        )

    def get_or_create_label_for_judge(self, judge):
        obj, created = EvidenceLabel.objects.get_or_create(
            evidence_candidate=self, judge=judge,
            labeled_by_machine=False, defaults={'label': None})
        return obj

    def set_label(self, label, judge):
        evidence_label, created = EvidenceLabel.objects.get_or_create(
            evidence_candidate=self,
            judge=judge,
        )
        evidence_label.label = label
        evidence_label.save()


class EvidenceLabel(BaseModel):
    NORELATION = "NO"
    YESRELATION = "YE"
    DONTKNOW = "DK"
    SKIP = "SK"
    NONSENSE = "NS"
    LABEL_CHOICES = (
        (NORELATION, "No relation present"),
        (YESRELATION, "Yes, relation is present"),
        (DONTKNOW, "Don't know if the relation is present"),
        (SKIP, "Skipped labeling of this evidence"),
        (NONSENSE, "Evidence is nonsense")
    )
    NEED_RELABEL = (
        # list of evidence labels that means it would be good to ask again
        DONTKNOW, SKIP
    )

    evidence_candidate = models.ForeignKey(
        'EvidenceCandidate',
        related_name='labels'
    )
    label = models.CharField(
        max_length=2, choices=LABEL_CHOICES,
        default=SKIP, null=True, blank=False
    )

    modification_date = models.DateTimeField(auto_now=True)

    # The judge field is meant to be the username of the person that decides
    # the label of this evidence. It's not modelled as a foreign key to allow
    # easier interaction with non-django code.
    judge = models.CharField(max_length=CHAR_MAX_LENGHT)
    labeled_by_machine = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        unique_together = ['evidence_candidate', 'label', 'judge']


# Models utils

def remove_invalid_segments():
    """
    Removes all segments that doesn't have two entity occurences
    because they are useless.
    """

    segments = list(TextSegment.objects.all())
    for segment in segments:
        eos = list(segment.get_entity_occurrences())
        if len(eos) < 2:
            segment.delete()
