from mongoengine import connect as mongoconnect

from iepy.models import (IEDocument, PreProcessSteps, InvalidPreprocessSteps,
    TextChunk)


def connect(db_name):
    mongoconnect(db_name)

class DocumentManager(object):

    ### Basic administration and pre-process

    def create_document(self, identifier, text, metadata=None):
        """Creates a new Document with text ready to be inserted on the
        information extraction pipeline (ie, ready to be tokenized, POS Tagged,
        etc).

        Identifier must be a unique value that will be used for distinguishing
        one document from another. If no title is given, will be inferred from
        the identifier.
        Metadata is a dictionary where you can put whaever you want to persist
        with your document. IEPy will do nothing with it except guarranting that
        such information will be preserved.
        """
        if metadata is None:
            metadata = {}
        doc = IEDocument(human_identifier=identifier, text=text, metadata=metadata)
        doc.save()
        return doc

    def get_raw_documents(self):
        """returns an interator of documents that lack the text field, or it's
        empty.
        """
        return IEDocument.objects(text='')

    def get_documents_lacking_preprocess(self, step):
        """Returns an iterator of documents that shall be processed on the given
        step."""
        if not isinstance(step, PreProcessSteps):
            raise InvalidPreprocessSteps
        query = {'preprocess_metadata__%s__exists' % step.name: False}
        return IEDocument.objects(**query)

    ### Accessors, filters and projections used on IE itself

    def documents_with_both_entities(self, entity_a, entity_b):
        """Returns an iterator of tuples (document, presence, presence)
        where there's at least a presence of entity_b preceeded by the
        presence of the entity_a.
        """
        pass

    def expand_entities_presence(self, document, presence_a, presence_b):
        """
        Returns a human readable representation of the text where some entities
        co-exist.
        """
        pass

class TextChunkManager(object):

    def chunks_with_both_entities(self, entity_a, entity_b):
        key_a, key_b = entity_a.key, entity_b.key
        return TextChunk.objects(entities__key=key_a)(entities__key=key_b)

