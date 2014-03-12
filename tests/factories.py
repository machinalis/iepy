import logging
import factory

from iepy.models import IEDocument, Entity


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

