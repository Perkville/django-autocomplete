from django import forms
from django.db import models

from autocomplete import widgets
from autocomplete.views import view as default_view


def autocomplete_formfield(ac_id, formfield=None, view=default_view,
        widget_class=None, multiple_widget_class=None, **kwargs):
    """
    >>> # uses the default formfield (CharField)
    >>> autocomplete_formfield('myapp.email')

    >>> # uses a custom formfield
    >>> autocomplete_formfield('myapp.email', forms.EmailField)

    >>> # uses ForeignKey.formfield
    >>> autocomplete_formfield(Message.user)

    >>> # uses ManyToManyField.formfield
    >>> autocomplete_formfield(User.permissions)

    Use a custom view::
        >>> autocomplete_formfield('myapp.ac_id', view=my_autocomplete_view)
        
    """
    kwargs.pop('request', None) # request can be passed by contrib.admin
    db = kwargs.get('using')
    settings = view.get_settings(ac_id)

    if formfield is None:
        formfield = getattr(settings.field, 'formfield', forms.CharField)

    if isinstance(settings.field, models.ForeignKey):
        kwargs['widget'] = widget_class(ac_id, view, using=db)
        kwargs['to_field_name'] = settings.key
    elif isinstance(settings.field, models.ManyToManyField):
        kwargs['widget'] = multiple_widget_class(ac_id, view, using=db)
        kwargs['to_field_name'] = settings.key
    else:
        js_options = dict(force_selection=False)
        js_options.update(settings.js_options)
        kwargs['widget'] = widget_class(ac_id, view, using=db, **js_options)

    return formfield(**kwargs)


def autocompleteform_factory():
    """Implement me!"""
