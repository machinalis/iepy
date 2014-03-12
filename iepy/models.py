from datetime import datetime

from enum import Enum
from mongoengine import DynamicDocument, fields


class PreProcessSteps(Enum):
    tokenization = 1
    segmentation = 2
    tagging = 3
    nerc = 4


class InvalidPreprocessSteps(Exception):
    pass


ENTITY_KINDS = (
    ('person', u'Person'),
    ('location', u'Location'),
    ('organization', u'Organization')
)


class Entity(DynamicDocument):
    string = fields.StringField()
    kind = fields.StringField(choices=ENTITY_KINDS)

    def __unicode__(self):
        return u'%s (%s)' % (self.string, self.kind)


class TextChunk(DynamicDocument):
    document = fields.ReferenceField('IEDocument', required=True)
    text = fields.StringField(required=True)

    tokens = fields.ListField(fields.StringField())
    sentences = fields.ListField(fields.IntField())  # not sure what it's in here
    postags = fields.ListField(fields.StringField())

    # Maybe this field needs to be de-normalized
    entities = fields.ListField(fields.ReferenceField('Entity'))


class IEDocument(DynamicDocument):
    human_identifier = fields.StringField(required=True, unique=True)
    title = fields.StringField()
    url = fields.URLField()
    text = fields.StringField()
    creation_date = fields.DateTimeField(default=datetime.now)
    # anything else you want to storein here that can be useful
    metadata = fields.DictField()

    # Fields and stuff that is computed while traveling the pre-process pipeline
    preprocess_metadata = fields.DictField()
    tokens = fields.ListField(fields.StringField())
    sentences = fields.ListField(fields.IntField())  # it's a list of token-offsets
    postags = fields.ListField(fields.StringField())
    entities = fields.ListField(fields.ReferenceField('Entity'))
    meta = {'collection': 'iedocuments'}

    # Mapping of preprocess steps and fields where the result is stored.
    preprocess_fields_mapping = {
        PreProcessSteps.tokenization: 'tokens',
        PreProcessSteps.segmentation: 'sentences',
        PreProcessSteps.tagging: 'postags',
    }

    def was_preprocess_done(self, step):
        return step.name in self.preprocess_metadata.keys()

    def set_preprocess_result(self, step, result):
        """Set the result in the internal representation.
        Explicit save must be triggered after this call.
        """
        if not isinstance(step, PreProcessSteps):
            raise InvalidPreprocessSteps
        if step == PreProcessSteps.segmentation:
            if filter(lambda x: not isinstance(x, int), result):
                raise ValueError('Segmentation result shall only contain ints')
            if sorted(result) != result:
                raise ValueError('Segmentation result shall be ordered.')
            if len(set(result)) < len(result):
                raise ValueError(
                    'Segmentation result shall not contain duplicates.')
            if result[0] != 0 or result[-1] != len(self.tokens):
                raise ValueError(
                    'Segmentation result must be offsets of tokens.')
        elif step == PreProcessSteps.tagging:
            if len(result) != len(self.tokens):
                raise ValueError(
                    'Tagging result must have same cardinality than tokens')

        field_name = self.preprocess_fields_mapping[step]
        setattr(self, field_name, result)
        self.preprocess_metadata[step.name] = {
            'done_at': datetime.now(),
        }
        return self  # So it's easily chainable with a .save() if desired

    def get_preprocess_result(self, step):
        """Returns the stored result for the asked preprocess step.
        If such result was never set, None will be returned instead"""
        if not self.was_preprocess_done(step):
            return None
        else:
            field_name = self.preprocess_fields_mapping[step]
            return getattr(self, field_name)

