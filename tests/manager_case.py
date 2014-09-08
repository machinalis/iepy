from unittest import TestCase

from mongoengine.connection import get_connection, disconnect

from iepy.data.db import connect


class ManagerTestCase(TestCase):
    """
        TestCase class that clear the collection between the tests
    """
    mongodb_name = 'test_mongo_engine'

    @classmethod
    def setUpClass(cls):
        disconnect()
        connect(cls.mongodb_name)
        cls.manager = cls.ManagerClass()

    def setUp(self):
        from mongoengine.connection import get_db
        db = get_db()
        for cname in db.collection_names():
            if cname != 'system.indexes':
                db.drop_collection(cname)
        super(ManagerTestCase, self).setUp()

    @classmethod
    def tearDownClass(cls):
        connection = get_connection()
        connection.drop_database(cls.mongodb_name)
        disconnect()
