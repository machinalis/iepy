# This module is the nexus/connection between the UI definitions (django models)
# and the IEPY models. Modifications of this file will be with the awareness of
# this dual-impact.
from django.db import models

from corpus.fields import ListField
import jsonfield

CHAR_MAX_LENGHT = 256


class EntityKind(models.Model):
    # There's a fixture declaring an initial set of Entity Kinds, containing
    # PERSON, LOCATION, AND ORGANIZATION
    name = models.CharField(max_length=CHAR_MAX_LENGHT, unique=True)

    class Meta:
        ordering = ['name']


class Entity(models.Model):
    key = models.CharField(max_length=CHAR_MAX_LENGHT)
    canonical_form = models.CharField(max_length=CHAR_MAX_LENGHT)
    kind = models.ForeignKey(EntityKind)

    class Meta:
        ordering = ['kind', 'key', 'canonical_form']
        unique_together = (('key', 'kind'), )

    def __unicode__(self):
        return u'%s (%s)' % (self.key, self.kind.name)


class IEDocument(models.Model):
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
    tagging = models.DateTimeField(null=True, blank=True)
    ner = models.DateTimeField(null=True, blank=True)
    segmentation = models.DateTimeField(null=True, blank=True)

    # anything else you want to store in here that can be useful
    metadata = jsonfield.JSONField()

    def get_sentences(self):
        """Iterator over the sentences, each sentence being a list of tokens.
        """
        tokens = self.tokens
        sentences = self.sentences
        start = 0
        for i, end in enumerate(sentences[1:]):
            yield tokens[start:end]
            start = end


class EntityOccurrence(models.Model):
    """Models the occurrence of a particular Entity on a Document"""
    entity = models.ForeignKey('Entity')
    document = models.ForeignKey('IEDocument', related_name='entity_ocurrences')
    segments = models.ManyToManyField('TextSegment', related_name='entity_ocurrences')
    offset = models.IntegerField()  # Offset in tokens wrt to document
    offset_end = models.IntegerField()  # Offset in tokens wrt to document
    # Text of the occurrence, so if it's different than canonical_form, it's easy to see
    alias = models.CharField(max_length=CHAR_MAX_LENGHT)

    class Meta:
        ordering = ['document', 'offset', 'offset_end']

    def __unicode__(self):
        return u'{0} ({1}, {2})'.format(self.entity.key, self.offset, self.offset_end)


class TextSegment(models.Model):
    document = models.ForeignKey('IEDocument')
    text = models.TextField()
    offset = models.IntegerField()  # Offset in tokens wrt document
    offset_end = models.IntegerField()  # in tokens wrt document

    # Reversed fields:
    # entity_ocurrences = Reversed ManyToManyField of EntityOccurrence

    def __unicode__(self):
        return u'{0}'.format(' '.join(self.tokens))
