import os
import sys
import django
from django.conf import settings

# Version number reading ...

fname = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'version.txt')
with open(fname, encoding='utf-8') as filehandler:
    __version__ = filehandler.read().strip().replace("\n", "")
del fname


def setup(fuzzy_path=None, settings_prefix=None, _safe_mode=False):
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
            path = _actual_path(fuzzy_path)
            if settings_prefix is None:
                settings_prefix = path.rsplit(os.sep, 1)[1]
            sys.path.append(path)  # add to py-path the first
            os.environ['DJANGO_SETTINGS_MODULE'] = "{}_settings".format(settings_prefix)
            result = path
        django.setup()
        if not _safe_mode and settings.IEPY_VERSION != __version__:
            sys.exit(
                'Instance version is {} and current IEPY installation is {}.\n'
                'Run iepy --upgrade on the instance.'.format(settings.IEPY_VERSION,
                                                             __version__)
            )
        return result


def _actual_path(fuzzy_path):
    """
    Given the fuzzy_path path, walks-up until it finds a folder containing a
    iepy-instance, and that folder path is returned"""
    def _is_iepy_instance(folder_path):
        folder_name = os.path.basename(folder_path)
        expected_file = os.path.join(
            folder_path,
            "{}_settings.py".format(folder_name)
        )
        return os.path.exists(expected_file)

    # first, make sure we are handling an absolute path
    original = fuzzy_path   # used for debug
    fuzzy_path = os.path.abspath(fuzzy_path)
    while True:
        if _is_iepy_instance(fuzzy_path):
            return fuzzy_path
        else:
            parent = os.path.dirname(fuzzy_path)
            if parent == fuzzy_path:
                raise ValueError(
                    "There's no IEPY instance on the provided path {}".format(original))
            fuzzy_path = parent
