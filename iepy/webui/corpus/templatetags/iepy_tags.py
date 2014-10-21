# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)
