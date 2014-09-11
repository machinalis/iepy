# This module is the nexus/connection between the UI definitions (django models)
# and the IEPY models. Modifications of this file should be done with the
# awareness of this dual-impact.
from datetime import datetime

from django.db import models
from enum import Enum

from iepy.utils import unzip
from corpus.fields import ListField
import jsonfield

CHAR_MAX_LENGHT = 256


class PreProcessSteps(Enum):
    tokenization = 1
    sentencer = 2
    tagging = 3
    ner = 4
    segmentation = 5


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


class Entity(BaseModel):
    key = models.CharField(max_length=CHAR_MAX_LENGHT)
    canonical_form = models.CharField(max_length=CHAR_MAX_LENGHT)
    kind = models.ForeignKey(EntityKind)

    class Meta(BaseModel.Meta):
        ordering = ['kind', 'key', 'canonical_form']
        unique_together = (('key', 'kind'), )

    def __unicode__(self):
        return u'%s (%s)' % (self.key, self.kind.name)


class IEDocument(BaseModel):
    human_identifier = models.CharField(max_length=CHAR_MAX_LENGHT,
                                        unique=True)
    title = models.CharField(max_length=CHAR_MAX_LENGHT)
    url = models.URLField()
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    # The following 3 lists have 1 item per token
    tokens = ListField()  # strings
    offsets_to_text = ListField()  # ints, character offset for tokens
    postags = ListField()  # strings

    sentences = ListField()  # ints, it's a list of token-offsets

    # Reversed fields:
    # entities = Reversed ForeignKey of EntityOccurrence
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


class EntityOccurrence(BaseModel):
    """Models the occurrence of a particular Entity on a Document"""
    entity = models.ForeignKey('Entity')
    document = models.ForeignKey('IEDocument', related_name='entity_ocurrences')
    segments = models.ManyToManyField('TextSegment', related_name='entity_ocurrences')
    offset = models.IntegerField()  # Offset in tokens wrt to document
    offset_end = models.IntegerField()  # Offset in tokens wrt to document
    # Text of the occurrence, so if it's different than canonical_form, it's easy to see
    alias = models.CharField(max_length=CHAR_MAX_LENGHT)

    class Meta(BaseModel.Meta):
        ordering = ['document', 'offset', 'offset_end']

    def __unicode__(self):
        return u'{0} ({1}, {2})'.format(self.entity.key, self.offset, self.offset_end)


class TextSegment(BaseModel):
    document = models.ForeignKey('IEDocument')
    text = models.TextField()
    offset = models.IntegerField()  # Offset in tokens wrt document
    offset_end = models.IntegerField()  # in tokens wrt document

    # Reversed fields:
    # entity_ocurrences = Reversed ManyToManyField of EntityOccurrence

    class Meta(BaseModel.Meta):
        pass

    def __unicode__(self):
        return u'{0}'.format(' '.join(self.tokens))
