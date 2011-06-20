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
            widget=forms.TextInput(attrs={'size': 44}),
            help_text=_('try a scientific or common name'),
            )
