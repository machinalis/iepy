# -*- coding: utf-8 -*-

from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from iepy.data import models


@receiver(pre_delete, sender=models.EntityOccurrence)
def pre_eo_delete(sender, instance, **kwargs):
    instance_segments = list(instance.segments.all())
    if hasattr(sender, "_segments_to_check"):
        sender._segments_to_check[instance.id] = instance_segments
    else:
        sender._segments_to_check = {instance.id: instance_segments}


@receiver(post_delete, sender=models.EntityOccurrence)
def on_eo_delete(sender, instance, **kwargs):
    segments_to_check = sender._segments_to_check.get(instance.id)
    if segments_to_check:
        for segment in segments_to_check:
            eos = list(segment.get_entity_occurrences())
            if len(eos) < 2:
                segment.delete()
