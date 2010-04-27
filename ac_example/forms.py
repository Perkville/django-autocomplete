from django import forms
from django.contrib.auth.models import User, Message

from autocomplete.widgets import AutoCompleteWidget
from autocomplete.fields import ModelChoiceField

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message

    user = ModelChoiceField('user')

class ExampleForm(forms.Form):

    # an existent user
    an_existent_user = ModelChoiceField('user')

    # an existent username
    an_existent_username = forms.CharField(widget=AutoCompleteWidget('name'))
    # an username, either existent or not
    an_username = forms.CharField(
        widget=AutoCompleteWidget('name', force_selection=False))
