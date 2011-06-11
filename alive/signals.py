# -*- coding: utf-8 -*-

from django.db.models import signals
from django.template.defaultfilters import slugify

def slug_pre_save(signal, instance, sender, **kwargs):
    '''Cria slug antes de salvar.'''
    slug = slugify(instance.name)
    instance.slug = slug
