from django.forms.util import ValidationError
from django.forms import fields
from django.utils.translation import ugettext_lazy as _
from autocomplete import AutoCompleteWidget, autocomplete

class AutoCompleteField(fields.Field):

    default_error_messages = {
        'invalid_choice': _(u'Select a valid choice. That choice is not one of'
                            u' the available choices.'),
    } 
    
    def __init__(self, ac_name=None, force_selection=True,
                 view_name='autocomplete', *args, **kwargs):
        if not kwargs.get('widget'):
            kwargs['widget'] = AutoCompleteWidget(ac_name, force_selection, view_name)
        super(AutoCompleteField, self).__init__(*args, **kwargs)

    def clean(self, value):
        fields.Field.clean(self, value)
        if value in fields.EMPTY_VALUES:
            return None

        settings = autocomplete.settings[self.widget.ac_name]
        queryset = settings[0]
        key = settings[3]
        try:
            return queryset.get(**{key: value})
        except queryset.model.DoesNotExist:
            raise ValidationError(self.error_messages['invalid_choice'])
