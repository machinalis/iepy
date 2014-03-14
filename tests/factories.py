import logging
import factory
import nltk

from iepy.models import (IEDocument, Entity, PreProcessSteps, EntityInSegment,
    TextSegment)


# In general, we are not interested on the debug and info messages
# of Factory-Boy itself
logging.getLogger("factory").setLevel(logging.WARN)


class EntityFactory(factory.Factory):
    FACTORY_FOR = Entity
    key = factory.Sequence(lambda n: 'id:%i' % n)
    canonical_form = factory.Sequence(lambda n: 'Entity #%i' % n)
    kind = 'person'


class EntityInSegmentFactory(factory.Factory):
    FACTORY_FOR = EntityInSegment
    key = factory.Sequence(lambda n: 'id:%i' % n)
    canonical_form = factory.Sequence(lambda n: 'Entity #%i' % n)
    kind = 'person'
    offset = 0


class IEDocFactory(factory.Factory):
    FACTORY_FOR = IEDocument
    human_identifier = factory.Sequence(lambda n: 'doc_%i' % n)
    title = factory.Sequence(lambda n: 'Title for doc %i' % n)
    text = factory.Sequence(lambda n: 'Lorem ipsum yaba daba du! %i' % n)


class TextSegmentFactory(factory.Factory):
    FACTORY_FOR = TextSegment
    document = factory.SubFactory(IEDocFactory)
    text = factory.Sequence(lambda n: 'Lorem ipsum yaba daba du! %i' % n)
    offset = factory.Sequence(lambda n: n * 3)
    tokens = ['lorem', 'ipsum', 'dolor']
    postags = ['NN', 'NN', 'V']
    entities = []


class SegmentedIEDocFactory(IEDocFactory):
    FACTORY_FOR = IEDocument
    text = factory.Sequence(lambda n: 'Lorem ipsum. Yaba daba du! %i' % n)

    @factory.post_generation
    def init(self, create, extracted, **kwargs):
        tokens = []
        sentences = [0]
        for sent in nltk.sent_tokenize(self.text):
            sent_tokens = nltk.word_tokenize(sent)
            tokens.extend(sent_tokens)
            sentences.append(sentences[-1] + len(sent_tokens))

        self.set_preprocess_result(PreProcessSteps.tokenization, tokens)
        self.set_preprocess_result(PreProcessSteps.segmentation, sentences)
