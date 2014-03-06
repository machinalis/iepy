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
    text = fields.StringField()  # pure text, derived from raw_data
    acquisition_date = fields.DateTimeField(default=datetime.now)
    # anything else you want to storein here that can be useful
    metadata = fields.DictField()

    # things that are computed while traveling the pre-process pipeline
    tokens = fields.ListField(fields.StringField())
    sentences = fields.ListField(fields.StringField())
    entities = fields.ListField(fields.ReferenceField('Entity'))
    meta = {'collection': 'iedocuments'}
