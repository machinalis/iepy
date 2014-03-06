from mongoengine import connect as mongoconnect

from iepy.models import IEDocument, PreProcessSteps


class DocumentConnector(object):

    def __init__(self, db_name):
        self.db_name = db_name
        self.connect()

    def connect(self):
        mongoconnect(self.db_name)

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
        pass

    def get_documents_lacking_preprocess(self, step):
        """Returns an iterator of documents that shall be processed on the given
        step."""
        if not isinstance(step, PreProcessSteps):
            return None

    def store_preprocess_output(self, document, step, output):
        pass

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
