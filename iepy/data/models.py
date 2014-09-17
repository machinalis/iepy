# This module is the nexus/connection between the UI definitions (django models)
# and the IEPY models. Modifications of this file should be done with the
# awareness of this dual-impact.
from datetime import datetime
import itertools
import logging
from operator import attrgetter

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

    def __unicode__(self):
        return self.name


class Entity(BaseModel):
    # the "key" IS the "canonical-form". Alieses are stored on
    # Entity Occurrences
    key = models.CharField(max_length=CHAR_MAX_LENGHT)
    kind = models.ForeignKey(EntityKind)

    class Meta(BaseModel.Meta):
        ordering = ['kind', 'key']
        unique_together = (('key', 'kind'), )

    def __unicode__(self):
        return u'%s (%s)' % (self.key, self.kind.name)


class IEDocument(BaseModel):
    human_identifier = models.CharField(max_length=CHAR_MAX_LENGHT,
                                        unique=True)
    title = models.CharField(max_length=CHAR_MAX_LENGHT)  # TODO: remove
    url = models.URLField()  # TODO: remove
    text = models.TextField()  # TODO: remove
    creation_date = models.DateTimeField(auto_now_add=True)

    # The following 3 lists have 1 item per token
    tokens = ListField()  # strings
    offsets_to_text = ListField()  # ints, character offset for tokens
    postags = ListField()  # strings

    sentences = ListField()  # ints, it's a list of token-offsets

    # Reversed fields:
    # entitiy_occurrences = Reversed ForeignKey of EntityOccurrence
    # text_segments = Reversed ForeignKey of TextSegment

    # Metadata annotations that're computed while traveling the pre-process pipeline
    tokenization_done_at = models.DateTimeField(null=True, blank=True)
    sentencer_done_at = models.DateTimeField(null=True, blank=True)
    tagging_done_at = models.DateTimeField(null=True, blank=True)
    ner_done_at = models.DateTimeField(null=True, blank=True)
    segmentation_done_at = models.DateTimeField(null=True, blank=True)

    # anything else you want to store in here that can be useful
    metadata = jsonfield.JSONField(blank=True)

    class Meta(BaseModel.Meta):
        pass

    def __unicode__(self):
        return u'<IEDocument {0}>'.format(self.human_identifier)

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

    def was_preprocess_step_done(self, step):
        return getattr(self, '%s_done_at' % step.name) is not None

    def set_tokenization_result(self, value):
        """Sets the value to the correspondent storage format"""
        if not isinstance(value, list):
            raise ValueError("Tokenization expected result should be a list "
                             "of tuples (token-string, token-offset on text (int)).")
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
            TextSegment.objects.bulk_create(zip(*new_segs)[0])
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

    def __unicode__(self):
        return u'{0} ({1}, {2})'.format(self.entity.key, self.offset, self.offset_end)

    def hydrate_for_segment(self, segment):
        # creates some on-memory attributes with respect to the segment
        self.segment_offset = self.offset - segment.offset
        self.segment_offset_end = self.offset_end - segment.offset_end
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

    def hydrate(self):
        # Using the segment offsets, and the data on document itself, constructs
        # on-memory attributes for the segment
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
        return self

    def get_entity_occurrences(self):
        """Returns an iterable of EntityOccurrences, sorted by offset"""
        return map(lambda eo: eo.hydrate_for_segment(self),
                   self.entity_occurrences.all().order_by('offset')
                   )

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

    def __unicode__(self):
        # return u'{0}'.format(' '.join(self.tokens))  # TODO: no tokens
        return u'({0} {1})'.format(self.offset, self.offset_end)


class Relation(BaseModel):
    name = models.CharField(max_length=CHAR_MAX_LENGHT)
    left_entity_kind = models.ForeignKey('EntityKind', related_name='left_relations')
    right_entity_kind = models.ForeignKey('EntityKind', related_name='right_relations')

    # Reversed fields:
    # evidence_relations = Reversed ForeignKey of LabeledRelationEvidence

    def __str__(self):
        return '{}({}, {})'.format(self.name, self.left_entity_kind,
                                   self.right_entity_kind)


class LabeledRelationEvidence(BaseModel):
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

    left_entity_occurrence = models.ForeignKey('EntityOccurrence',
                                               related_name='left_evidence_relations')
    right_entity_occurrence = models.ForeignKey('EntityOccurrence',
                                                related_name='right_evidence_relations')
    relation = models.ForeignKey('Relation', related_name='evidence_relations')
    segment = models.ForeignKey('TextSegment')
    label = models.CharField(max_length=2, choices=LABEL_CHOICES, default=SKIP)

    date = models.DateTimeField(auto_now_add=True)
    # The judge field is meant to be the username of the person that decides
    # the label of this evidence. It's not modelled as a foreign key to allow
    # easier interaction with non-django code.
    judge = models.CharField(max_length=CHAR_MAX_LENGHT)

    def __str__(self):
        s = "In '{}' for the relation '{}({}, {})' the user {} answered: {}"
        return s.format(self.segment, self.relation.name,
                        self.left_entity_occurrence.alias,
                        self.right_entity_occurrence.alias,
                        self.judge, self.label)
        return u'({0} {1})'.format(self.offset, self.offset_end)
