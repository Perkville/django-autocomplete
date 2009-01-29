from django import forms
from django.contrib.auth.models import User, Message
import autocomplete as ac

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message

    user = ac.ModelChoiceField('user')

class ExampleForm(forms.Form):

    # an existent user
    an_existent_user = ac.ModelChoiceField('user')

    # an existent username
    an_existent_username = forms.CharField(widget=ac.AutoCompleteWidget('name'))
    # an username, either existent or not
    an_username = forms.CharField(widget=ac.AutoCompleteWidget('name', False))
