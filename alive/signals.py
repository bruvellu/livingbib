# -*- coding: utf-8 -*-

from django.db.models import signals
from django.template.defaultfilters import slugify

def slug_pre_save(signal, instance, sender, **kwargs):
    '''Create slug before saving.'''
    slug = slugify(instance.name)
    instance.slug = slug

def update_delta(signal, instance, sender, **kwargs):
    '''Update variation of total results for taxon query.'''
    try:
        delta = instance.total_results - instance.taxon.total_results
        instance.delta = delta
    except:
        instance.delta = 0

def update_results(signal, instance, sender, **kwargs):
    '''Update total number of results for taxon query.'''
    instance.taxon.total_results = instance.total_results
    instance.taxon.delta = instance.delta
    instance.taxon.save()
