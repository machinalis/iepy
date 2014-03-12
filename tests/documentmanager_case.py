from unittest import TestCase

from mongoengine.connection import get_connection, disconnect

from iepy.db import DocumentManager, connect


class DocumentManagerTestCase(TestCase):
    """
        TestCase class that clear the collection between the tests
    """
    mongodb_name = 'test_mongo_engine'

    @classmethod
    def setUpClass(cls):
        disconnect()
        connect(cls.mongodb_name)
        cls.manager = DocumentManager()

    def setUp(self):
        from mongoengine.connection import get_db
        db = get_db()
        for cname in db.collection_names():
            if cname != 'system.indexes':
                db.drop_collection(cname)
        super(DocumentManagerTestCase, self).setUp()

    @classmethod
    def tearDownClass(cls):
        connection = get_connection()
        connection.drop_database(cls.mongodb_name)
        disconnect()
