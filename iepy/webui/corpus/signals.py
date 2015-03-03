# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
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


@receiver(pre_delete, sender=models.GazetteItem)
def pre_gazette_delete(sender, instance, **kwargs):
    to_delete = list(instance.entity_set.all())
    sender.to_delete = to_delete


@receiver(post_delete, sender=models.GazetteItem)
def on_gazette_delete(sender, instance, **kwargs):
    if hasattr(sender, "to_delete"):
        for entity in sender.to_delete:
            entity.delete()


@receiver(post_delete, sender=models.Entity)
def on_entity_delete(sender, instance, **kwargs):
    if instance.gazette:
        instance.gazette.delete()


@receiver(pre_delete, sender=models.IEDocument)
def pre_iedocument_delete(sender, instance, **kwargs):
    to_delete = [instance.metadata]
    sender.to_delete = to_delete


@receiver(post_delete, sender=models.IEDocument)
def on_iedocument_delete(sender, instance, **kwargs):
    if hasattr(sender, "to_delete"):
        for item in sender.to_delete:
            item.delete()
