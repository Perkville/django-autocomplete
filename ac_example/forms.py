from django import forms
from django.contrib.auth.models import User, Message
from autocomplete import AutoCompleteWidget, AutoCompleteField

class InsertMessage(forms.ModelForm):
    class Meta:
        model = Message

    user = forms.ModelChoiceField(User.objects.all(),
            widget=AutoCompleteWidget('user'), help_text="you must select a valid choice")

    other_user = AutoCompleteField('user')
    username = forms.CharField(widget=AutoCompleteWidget('user', force_selection=False))
