import os
import django
from django.conf import settings


def setup():
    if not settings.configured:
        if not os.getenv('DJANGO_SETTINGS_MODULE'):
            os.environ['DJANGO_SETTINGS_MODULE'] = 'iepy.webui.webui.settings'
        django.setup()
