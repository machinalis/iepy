from datetime import datetime

from enum import Enum
from mongoengine import DynamicDocument, EmbeddedDocument, fields

from iepy.utils import unzip


class PreProcessSteps(Enum):
    tokenization = 1
    sentencer = 2
    tagging = 3
    nerc = 4
    segmentation = 5


class InvalidPreprocessSteps(Exception):
    pass


ENTITY_KINDS = (
    ('person', u'Person'),
    ('location', u'Location'),
    ('organization', u'Organization')
)


def _interval_offsets(a, xl, xr, lo=0, hi=None, key=None):
    """
    Given a sorted list/tuple/array a, returns a pair (l,r) that satisfies:

    all(v < xl for v in a[lo:l])
    all(xl <= v < xr for v in a[l:r])
    all(xr <= v for v in a[r:hi])

    key(v) is used if key is provided
    default value for hi is len(a)
    """
    # Default key: identity
    if key is None: key = lambda x: x
    if hi is None: hi = len(a)
    if lo < 0:
        raise ValueError("lo must not be negative")
    if xl > xr:
        raise ValueError("This function requires xl <= xr ")
    # Special case: empty range:
    if lo == hi:
        return lo, hi
    # Reduce range for both left and right endpoints
    while lo < hi:
        mid = (lo + hi) // 2
        v = key(a[mid])
        if xl <= v and xr <= v:
            hi = mid
        elif v < xl and v < xr:
            lo = mid + 1
        else:
            # xl <= v < xr; now we need to split left and right intervals
            break
    llo, lhi = lo, mid
    rlo, rhi = mid, hi
    # Find left bisection point
    while llo < lhi:
        mid = (llo + lhi) // 2
        if key(a[mid]) < xl:
            llo = mid + 1
        else:
            lhi = mid
    # Find right bisection point
    while rlo < rhi:
        mid = (rlo + rhi) // 2
        if xr <= key(a[mid]):
            rhi = mid
        else:
            rlo = mid + 1
    return (llo, rlo)


class Entity(DynamicDocument):
    key = fields.StringField(required=True, unique=True)
    canonical_form = fields.StringField(required=True)
    kind = fields.StringField(choices=ENTITY_KINDS)

    def __unicode__(self):
        return u'%s (%s)' % (self.string, self.kind)


class EntityOccurrence(EmbeddedDocument):
    entity = fields.ReferenceField('Entity', required=True)
    offset = fields.IntField(required=True)  # Offset in tokens wrt to document
    offset_end = fields.IntField(required=True)  # Offset in tokens wrt to document
    alias = fields.StringField()  # Text of the occurrence, if different than canonical_form


class EntityInSegment(EmbeddedDocument):
    key = fields.StringField(required=True)
    canonical_form = fields.StringField(required=True)
    kind = fields.StringField(choices=ENTITY_KINDS, required=True)
    offset = fields.IntField(required=True)  # Offset in tokens wrt to segment
    offset_end = fields.IntField(required=True)  # Offset in tokens wrt to segment
    alias = fields.StringField()  # Representation of the entity actually used in the text


class TextSegment(DynamicDocument):
    document = fields.ReferenceField('IEDocument', required=True)
    text = fields.StringField(required=True)
    offset = fields.IntField()  # Offset in tokens wrt document

    # The following lists have the same length, correspond 1-to-1
    tokens = fields.ListField(fields.StringField())
    postags = fields.ListField(fields.StringField())

    entities = fields.ListField(fields.EmbeddedDocumentField(EntityInSegment))

    @classmethod
    def build(cls, document, token_offset, token_offset_end):
        """
        Build a segment based in the given documents, using the tokens in the
        range [token_offset:token_offset_end] (note that this has the usual
        python-range semantics)

        use the given text as reference (it should be a human readable
        representation of the segment
        """
        self = cls()
        self.document = document
        self.offset = token_offset
        self.tokens = document.tokens[token_offset:token_offset_end]
        self.postags = document.postags[token_offset:token_offset_end]
        if token_offset < len(document.offsets):
            text_start = document.offsets[token_offset]
        else:
            text_start = len(document.text)
        if token_offset_end < len(document.offsets):
            text_end = document.offsets[token_offset_end]
        else:
            text_end = len(document.text)
        self.text = document.text[text_start:text_end]
        l, r = _interval_offsets(
            document.entities,
            token_offset, token_offset_end,
            key=lambda occ: occ.offset)
        entities = []
        for o in document.entities[l:r]:
            entities.append(EntityInSegment(
                key=o.entity.key,
                canonical_form=o.entity.canonical_form,
                kind=o.entity.kind,
                offset=o.offset - token_offset,
                offset_end=o.offset_end - token_offset,
                alias=o.alias,
            ))
        self.entities = entities
        return self


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

    # The following 3 lists have 1 item per token
    tokens = fields.ListField(fields.StringField())
    offsets = fields.ListField(fields.IntField())  # character offset for tokens
    postags = fields.ListField(fields.StringField())

    sentences = fields.ListField(fields.IntField())  # it's a list of token-offsets
    # Occurrences of entites, sorted by offset
    entities = fields.ListField(fields.EmbeddedDocumentField(EntityOccurrence))
    meta = {'collection': 'iedocuments'}

    # Mapping of preprocess steps and fields where the result is stored.
    preprocess_fields_mapping = {
        PreProcessSteps.tokenization: ('offsets', 'tokens'),
        PreProcessSteps.sentencer: 'sentences',
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
        if step == PreProcessSteps.sentencer:
            if filter(lambda x: not isinstance(x, int), result):
                raise ValueError('Sentencer result shall only contain ints')
            if sorted(result) != result:
                raise ValueError('Sentencer result shall be ordered.')
            if len(set(result)) < len(result):
                print result
                raise ValueError(
                    'Sentencer result shall not contain duplicates.')
            if result[0] != 0 or result[-1] != len(self.tokens):
                raise ValueError(
                    'Sentencer result must be offsets of tokens.')
        elif step == PreProcessSteps.tagging:
            if len(result) != len(self.tokens):
                raise ValueError(
                    'Tagging result must have same cardinality than tokens')

        field_name = self.preprocess_fields_mapping[step]
        if isinstance(field_name, tuple):
            # Some steps are stored on several fields
            names = field_name
            results = unzip(result, len(names))
            for field_name, result in zip(names, results):
                setattr(self, field_name, result)
        else:
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
        if isinstance(field_name, tuple):
            # Some steps are stored on several fields
            names = field_name
            results = []
            for field_name in names:
                results.append(getattr(self, field_name))
            return zip(*results)
        else:
            return getattr(self, field_name)

    def get_sentences(self):
        """Iterator over the sentences, each sentence being a list of tokens.
        """
        tokens = self.tokens
        sentences = self.sentences
        start = 0
        for i, end in enumerate(sentences[1:]):
            yield tokens[start:end]
            start = end


