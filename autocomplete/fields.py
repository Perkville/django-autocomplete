from django import forms
from autocomplete import autocomplete, AutoCompleteWidget

class ModelChoiceField(forms.ModelChoiceField):
    widget = AutoCompleteWidget

    def __init__(self, ac_name, reverse_label=True, view_name='autocomplete', **kwargs):
        self.ac_name = ac_name
        self.widget = self.widget(ac_name, True, reverse_label, view_name)
        forms.Field.__init__(self, **kwargs)

    def _get_queryset(self):
        return autocomplete.settings[self.ac_name][0]
    queryset = property(_get_queryset, forms.ModelChoiceField._set_queryset)

    @property
    def to_field_name(self):
        return autocomplete.settings[self.ac_name][3]
