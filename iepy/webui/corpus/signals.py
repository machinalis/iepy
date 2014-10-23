# -*- coding: utf-8 -*-

from django.db.models.signals import post_delete
from django.dispatch import receiver
from iepy.data import models


@receiver(post_delete, sender=models.EntityOccurrence)
def on_eo_delete(sender, **kwargs):
    models.remove_invalid_segments()
