import os
import sys
import django
from django.conf import settings


def setup(path=None, settings_prefix=None):
    if not settings.configured:
        if path is None:
            if not os.getenv('DJANGO_SETTINGS_MODULE'):
                os.environ['DJANGO_SETTINGS_MODULE'] = 'iepy.webui.webui.settings'
        else:
            if settings_prefix is None:
                settings_prefix = path.rsplit(os.sep, 1)[1]
            sys.path.append(path) # add to the first
            os.environ['DJANGO_SETTINGS_MODULE'] = "{}_settings".format(settings_prefix)

        django.setup()
