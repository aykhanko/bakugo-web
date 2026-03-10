from django import forms
from django.utils.translation import gettext_lazy as _


class RoutePlannerForm(forms.Form):
    origin = forms.CharField(
        max_length=200,
        label=_('From'),
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter origin stop or area',
            'autocomplete': 'off',
        })
    )
    destination = forms.CharField(
        max_length=200,
        label=_('To'),
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter destination stop or area',
            'autocomplete': 'off',
        })
    )
