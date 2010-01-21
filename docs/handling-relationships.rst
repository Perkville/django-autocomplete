Quickstart: Handling relationships
==================================

the Django AutoComplete's :class:`~autocomplete.fields.ModelChoiceField` can be
used to handle relationships between models. It's a subclass of  the Django's
`ModelChoiceField`_ and uses :class:`~autocomplete.widgets.AutoCompleteWidget`
as the default widget.

Let's assume we have a form to send a message to an user::

    from django import forms
    from django.contrib.auth.models import User

    class MessageForm(forms.Form):
        user = forms.ModelChoiceField(User.objects.all())
        message = forms.CharField(widget=forms.Textarea)

.. note::
    
    You could obtain the same form using a `ModelForm`_ with the
    :class:`!django.contrib.auth.models.Message` model.
    
.. _`ModelChoiceField`: http://docs.djangoproject.com/en/dev/ref/forms/fields/#modelchoicefield
.. _`ModelForm`: http://docs.djangoproject.com/en/dev/topics/forms/modelforms/#modelform


Using AutoComplete with the Form
--------------------------------

But what if we have *a lot* of users?
Finding the right one within a :class:`~forms.Select` would be frustrating and
moreover would result in a heavy query (``SELCT * FROM auth_user``) every time
the form is displayed. That's why we prefer to use AutoComplete::

    from django import forms
    from autocomplete import ModelChoiceField

    class MessageForm(forms.Form):
        user = ModelChoiceField('user')
        message = forms.CharField(widget=forms.Textarea)

The string ``'user'`` passed as the first parameter of
:class:`~autocomplete.fields.ModelChoiceField` is an
identifier used by autocomplete to select the correct choices-set to render.


Defining a choices-set
----------------------

We must define this choices-set editing our URLConf as follows::

    from django.contrib.auth.models import User
    from autocomplete.views import autocomplete

    autocomplete.register(
        id = 'user',
        queryset = User.objects.all(),
        fields = ('username', 'email'),
        limit = 5,
    )

This registers the ``user`` choices-set and maps to it a queryset containing all
the users in our database (``User.objects.all()``). It will also filter the
results by the ``username`` and ``email`` fields and display at most five users per
query.


Registering the autocomplete view
---------------------------------

Now to let AutoComplete serve our choices as json data, we have to register the
autocomplete view::

    urlpatterns = patterns('',
        # your urls here ...
        url('^autocomplete/(\w+)/$', autocomplete, name='autocomplete'),
        # ... and other urls here.
    )

Ok. That's it. Just render the form in a template and enjoy.

.. seealso::

    :ref:`media-files-configuration`
        for how to configure and customize the
        Media files of your widget (including how to use `JQuery`_ or other js toolkits
        with Django AutoComplete).

.. _`JQuery`: http://jquery.com
