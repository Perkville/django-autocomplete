from django import forms

from django.contrib.auth.models import User, Message
from autocomplete.widgets import ModelAutoComplete

class InsertMessage(forms.ModelForm):
    class Meta:
        model = Message

    user = forms.ModelChoiceField(User.objects.all(),
            widget=ModelAutoComplete('user'))
