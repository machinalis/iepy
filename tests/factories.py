import logging
from tempfile import NamedTemporaryFile
import sys

import factory
import nltk

from iepy.data.knowledge import Fact, Evidence
from iepy.data.models import (IEDocument, EntityKind, Entity, EntityOccurrence,
                              TextSegment, Relation, LabeledRelationEvidence)


def naive_tkn(text):
    """Makes a naive tokenization returning pairs of tokens and
    offsets. Note, generated offsets are just numbers, to make things easy.
    """
    return list(enumerate(text.split()))


# In general, we are not interested on the debug and info messages
# of Factory-Boy itself
logging.getLogger("factory").setLevel(logging.WARN)

# declared like this to "facilitate" changing the ORM
BaseFactory = factory.django.DjangoModelFactory


class EntityKindFactory(BaseFactory):
    class Meta:
        model = 'corpus.EntityKind'
        django_get_or_create = ('name', )
    name = factory.Sequence(lambda n: 'kind_%i' % n)


class EntityFactory(BaseFactory):
    class Meta:
        model = 'corpus.Entity'
        django_get_or_create = ('key', 'kind', )
    key = factory.Sequence(lambda n: 'id:%i' % n)
    kind = factory.SubFactory(EntityKindFactory)


class EntityOccurrenceFactory(BaseFactory):
    FACTORY_FOR = EntityOccurrence
    entity = factory.SubFactory(EntityFactory)
    offset = 0
    offset_end = 1
    alias = ''


class IEDocFactory(BaseFactory):
    FACTORY_FOR = IEDocument
    human_identifier = factory.Sequence(lambda n: 'doc_%i' % n)
    title = factory.Sequence(lambda n: 'Title for doc %i' % n)
    text = factory.Sequence(lambda n: 'Lorem ipsum yaba daba du! %i' % n)


class TextSegmentFactory(BaseFactory):
    FACTORY_FOR = TextSegment
    document = factory.SubFactory(IEDocFactory)
    offset = factory.Sequence(lambda n: n * 3)
    offset_end = factory.Sequence(lambda n: n * 3 + 1)


class SentencedIEDocFactory(IEDocFactory):
    FACTORY_FOR = IEDocument
    text = factory.Sequence(lambda n: 'Lorem ipsum. Yaba daba du! %i' % n)

    @factory.post_generation
    def init(self, create, extracted, **kwargs):
        tokens = []
        sentences = [0]
        for sent in nltk.sent_tokenize(self.text):
            sent_tokens = nltk.word_tokenize(sent)
            tokens.extend(list(enumerate(sent_tokens)))
            sentences.append(sentences[-1] + len(sent_tokens))

        self.set_tokenization_result(tokens)
        self.set_sentencer_result(sentences)


class RelationFactory(BaseFactory):
    FACTORY_FOR = Relation
    name = factory.Sequence(lambda n: 'relation:%i' % n)
    left_entity_kind = factory.SubFactory(EntityKindFactory)
    right_entity_kind = factory.SubFactory(EntityKindFactory)


def NamedTemporaryFile23(*args, **kwargs):
    """Works exactly as a wrapper to tempfile.NamedTemporaryFile except that
       in python2.x, it excludes the "encoding" parameter when provided."""
    if sys.version_info[0] == 2:  # Python 2
        kwargs.pop('encoding', None)
    return NamedTemporaryFile(*args, **kwargs)


class FactFactory(factory.Factory):
    # TODO: This shall be removed/replaced when finished relation-storage branch
    FACTORY_FOR = Fact
    e1 = factory.SubFactory(EntityFactory)
    e2 = factory.SubFactory(EntityFactory)
    relation = factory.Sequence(lambda n: 'relation:%i' % n)


class EvidenceFactory(BaseFactory):
    """Factory for Evidence instances()

    In addition to the usual Factory Boy behavior, this factory also accepts a
    'markup' argument. The markup is a string with the tokens of the text
    segment separated by entities. You can flag entities by entering them as
    {token token token|kind}. You can also use kind* to flag the first/right
    occurrence used for the fact, and kind** to flag the second/left.

    For example, the following is valid markup:

    "The physicist {Albert Einstein|Person*} was born in {Germany|location} and
    died in the {United States|location**} ."
    """
    FACTORY_FOR = LabeledRelationEvidence
    relation = factory.SubFactory(RelationFactory)
    segment = factory.SubFactory(TextSegmentFactory)
    right_entity_occurrence = factory.SubFactory(
        EntityOccurrenceFactory,
        entity__kind=factory.SelfAttribute('...relation.right_entity_kind'),
        document=factory.SelfAttribute('..segment.document')
    )
    left_entity_occurrence = factory.SubFactory(
        EntityOccurrenceFactory,
        entity__kind=factory.SelfAttribute('...relation.left_entity_kind'),
        document=factory.SelfAttribute('..segment.document')
    )
    label = None

    @classmethod
    def create(cls, **kwargs):
        def eo_args(tokens, eotokens, kind):
            txt = ' '.join(eotokens)
            return {
                'entity__key': txt,
                'entity__kind__name': kind,
                'alias': txt,
                'offset': len(tokens),
                'offset_end': len(tokens) + len(eotokens)
            }
        args = {}
        markup = kwargs.pop('markup', None)
        if markup is not None:
            # will consider the document as having exactly the same than this segment
            tokens = []
            e_occurrences = []
            while markup:
                if markup.startswith("{"):
                    closer = markup.index("}")
                    entity = markup[1:closer]
                    markup = markup[closer+1:].lstrip()
                    eotokens, eokind = entity.split('|')
                    eotokens = eotokens.split()
                    eo_flags = eokind.count('*')
                    eokind = eokind.strip('*')
                    eo_args_ = eo_args(tokens, eotokens, eokind)

                    if eo_flags == 2:
                        args.update(
                            {'left_entity_occurrence__%s' % k: v
                             for k, v in eo_args_.items()}
                        )
                        args["relation__left_entity_kind__name"] = eokind
                    elif eo_flags == 1:
                        args.update(
                            {'right_entity_occurrence__%s' % k: v
                             for k, v in eo_args_.items()}
                        )
                        args["relation__right_entity_kind__name"] = eokind
                    else:
                        e_occurrences.append((eotokens, len(tokens), eokind))
                    tokens += eotokens
                elif ' ' in markup:
                    token, markup = markup.split(' ', 1)
                    tokens.append(token)
                else:
                    tokens.append(markup)
                    markup = ''
            args["segment__document__text"] = " ".join(tokens)
            args["segment__document__tokens"] = tokens
            args["segment__offset"] = 0
            args["segment__offset_end"] = len(tokens)
            args["e_occurrences"] = e_occurrences

        args.update(kwargs)
        return super(EvidenceFactory, cls).create(**args)

    @factory.post_generation
    def e_occurrences(self, create, extracted, **kwargs):
        doc = self.segment.document
        for eotokens, offset, kind_name in extracted:
            alias = ' '.join(eotokens)
            EntityOccurrenceFactory(
                entity__kind__name=kind_name,
                entity__key=alias,
                alias=alias,
                document=doc,
                offset=offset,
                offset_end=offset + len(eotokens),
            )
        # Now that all were created, check which shall be included for segment
        self.segment.entity_occurrences = doc.entity_occurrences.filter(
            offset__gte=self.segment.offset,
            offset_end__lte=self.segment.offset_end
        )
