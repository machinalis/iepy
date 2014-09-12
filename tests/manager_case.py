import unittest

from django.conf import settings
from django.test import TestCase
from django.test.utils import setup_test_environment, teardown_test_environment

import iepy

from django.test.runner import DiscoverRunner


class ManagerTestCase(TestCase):
    """
        TestCase class that clear the makes sure that the models created thru
        ORM are deleted between tests
    """

    # We are doing something not very clever, but fast enough (of coding):
    #   Emulate the django test runner. The downside is that all the environment
    #   and database stuff is setup once per TestCase (instead as it should, once
    #   per run)
    @classmethod
    def setUpClass(cls):
        # ORM environment and database setup
        iepy.setup()
        cls.dj_runner = DiscoverRunner()
        cls.dj_runner.setup_test_environment()
        cls.old_config = cls.dj_runner.setup_databases()
        # Creating Manager instance (if requested)
        if hasattr(cls, 'ManagerClass'):
            cls.manager = cls.ManagerClass()

    @classmethod
    def tearDownClass(cls):
        cls.dj_runner.teardown_databases(cls.old_config)
        cls.dj_runner.teardown_test_environment()
