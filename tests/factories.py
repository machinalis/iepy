#from datetime import datetime
import logging
import factory

from iepy.models import IEDocument, Entity, PreProcessSteps


# In general, we are not interested on the debug and info messages
# of Factory-Boy itself
logging.getLogger("factory").setLevel(logging.WARN)


class IEDocFactory(factory.Factory):
    FACTORY_FOR = IEDocument
    human_identifier = factory.Sequence(lambda n: 'doc_%i' % n)
    title = factory.Sequence(lambda n: 'Title for doc %i' % n)
    text = factory.Sequence(lambda n: 'Lorem ipsum yaba daba du! %i' % n)


class EntityFactory(factory.Factory):
    FACTORY_FOR = Entity
    key = factory.Sequence(lambda n: 'id:%i' % n)
    canonical_form = factory.Sequence(lambda n: 'Entity #%i' % n)
    kind = 'person'


class SegmentedIEDocFactory(factory.Factory):
    FACTORY_FOR = IEDocument
    human_identifier = factory.Sequence(lambda n: 'doc_%i' % n)
    title = factory.Sequence(lambda n: 'Title for doc %i' % n)
    text = factory.Sequence(lambda n: 'Lorem ipsum. Yaba daba du! %i' % n)
    
    @factory.post_generation
    def init(self, create, extracted, **kwargs):
        tokens = ['Lorem', 'ipsum', '.', 'Yaba', 'daba', 'du', '!', '%i']
        self.set_preprocess_result(PreProcessSteps.tokenization, tokens)
        sentences = [0, 3, 7, 8]
        self.set_preprocess_result(PreProcessSteps.segmentation, sentences)
        
    #tokens = factory.Sequence(lambda n: ['Lorem', 'ipsum', '.', 'Yaba', 'daba', 
    #                                                    'du', '!', '%i' % n])
    #sentences = [0, 3, 7, 8]
    #preprocess_metadata = { 
    #    PreProcessSteps.tokenization.name: { 'done_at': datetime.now() },
    #    PreProcessSteps.segmentation.name: { 'done_at': datetime.now() },
    #}

