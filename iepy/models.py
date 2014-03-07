from datetime import datetime

from enum import Enum
from mongoengine import DynamicDocument, fields


class PreProcessSteps(Enum):
    tokenization = 1
    segmentation = 2
    tagging = 3
    nerc = 4


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
    document_id = fields.ObjectIdField(required=True)
    text_chunk = fields.StringField(required=True)
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
    segments = fields.ListField(fields.StringField())
    entities = fields.ListField(fields.ReferenceField('Entity'))
    meta = {'collection': 'iedocuments'}

    def was_preprocess_done(self, step):
        return step.name in self.preprocess_metadata.keys()

    def set_preprocess_result(self, step, result):
        """Set the result in the internal representation.
        Explicit save mus be triggered after this call.
        """
        if step == PreProcessSteps.tokenization:
            self.tokens = result
        if step == PreProcessSteps.segmentation:
            self.segments = result
        self.preprocess_metadata[step.name] = {
            'done_at': datetime.now(),
        }

    def get_preprocess_result(self, step):
        """Returns the stored result for the asked preprocess step.
        If such result was never set, None will be returned instead"""
        if not self.was_preprocess_done(step):
            return None
        elif step == PreProcessSteps.tokenization:
            return self.tokens
        elif step == PreProcessSteps.segmentation:
            return self.segments
