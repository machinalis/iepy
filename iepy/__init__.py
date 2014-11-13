import os
import sys
from importlib import import_module

import django
from django.conf import settings

# Version number reading ...

fname = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'version.txt')
with open(fname, encoding='utf-8') as filehandler:
    __version__ = filehandler.read().strip().replace("\n", "")
del fname

instance = None  # instance reference will be stored here


def setup(fuzzy_path=None, _safe_mode=False):
    """
    Configure IEPY internals,
        Reads IEPY instance configuration if any path provided.
        Detects out of dated instances.
        Returns the absolute path to the IEPY instance if provided, None if not.
    """

    # Prevent nosetests messing up with this
    if not isinstance(fuzzy_path, (type(None), str)):
        # nosetests is grabing this function because its named "setup"... .
        return

    if not settings.configured:
        if fuzzy_path is None:
            if not os.getenv('DJANGO_SETTINGS_MODULE'):
                os.environ['DJANGO_SETTINGS_MODULE'] = 'iepy.webui.webui.settings'
            result = None
        else:
            path, project_name, old = _actual_path(fuzzy_path)
            sys.path.insert(0, path)
            if old:
                django_settings_module = "{0}_settings".format(project_name)
                sys.path.insert(0, os.path.join(path, project_name))
            else:
                django_settings_module = "{0}.settings".format(project_name)
            os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module
            result = os.path.join(path, project_name)
            import_instance(project_name)

        django.setup()

        if not _safe_mode and settings.IEPY_VERSION != __version__:
            sys.exit(
                'Instance version is {} and current IEPY installation is {}.\n'
                'Run iepy --upgrade on the instance.'.format(settings.IEPY_VERSION,
                                                             __version__)
            )
        return result


def import_instance(project_name):
    """
    Imports the project_name instance and stores it
    on the global variable `instance`.
    """

    global instance
    instance = import_module(project_name)


def _actual_path(fuzzy_path):
    """
    Given the fuzzy_path path, walks-up until it finds a folder containing a iepy-instance.
    Returns the path where the folder is contained, the folder name and a boolean to indicate
    if its an instance older than 0.9.2 where the settings file was different.
    """
    def _find_settings_file(folder_path):
        folder_name = os.path.basename(folder_path)
        expected_file = os.path.join(folder_path, "settings.py")
        old_settings_file = os.path.join(
            folder_path, "{}_settings.py".format(folder_name)
        )
        if os.path.exists(expected_file):
            return expected_file
        elif os.path.exists(old_settings_file):
            return old_settings_file

    # first, make sure we are handling an absolute path
    original = fuzzy_path   # used for debug
    fuzzy_path = os.path.abspath(fuzzy_path)
    while True:
        settings_filepath = _find_settings_file(fuzzy_path)
        if settings_filepath is not None:
            old = True if settings_filepath.endswith("_settings.py") else False
            return os.path.dirname(fuzzy_path), os.path.basename(fuzzy_path), old
        else:
            parent = os.path.dirname(fuzzy_path)
            if parent == fuzzy_path:
                raise ValueError("There's no IEPY instance on the provided path {}".format(original))
            fuzzy_path = parent
