# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

ORDER_BY = (
        ('stats__readers', _('readers')),
        ('title', _('title')),
        ('year', _('year')),
        ('rank', _('rank')),
        ('type', _('type')),
        ('publication_outlet', _('journal')),
        ('publisher', _('publisher')),
        )

class SortForm(forms.Form):
    type = forms.ChoiceField(choices=ORDER_BY, label=_('Sort by'))
    reverse = forms.BooleanField(required=False, initial=False, label=_('Reverse'))


class SearchForm(forms.Form):
    query = forms.CharField(
            label=_('Search for'),
            widget=forms.TextInput(attrs={'size': 32}),
            help_text=_('(type a taxon name (or common name))'),
            )
