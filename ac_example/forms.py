from django import forms
from django.contrib.auth.models import User, Message
from autocomplete.widgets import AutoComplete

class InsertMessage(forms.ModelForm):
    class Meta:
        model = Message

    user = forms.ModelChoiceField(User.objects.all(),
            widget=AutoComplete('user'), help_text="you must select a valid choice")
    username = forms.CharField(widget=AutoComplete('user', force_selection=False))
