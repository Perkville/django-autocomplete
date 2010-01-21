Quickstart: Handling suggestions
================================

AutoCompleteWidget can be used to offer *suggestions* based on the user input.
Let's assume for example that we have a Form to send mails to other users::

    from django import forms

    class SendMail(forms.Form):
        to = forms.EmailField()
        subject = forms.CharField(required=False)
        content = forms.CharField(widget=forms.Textarea)


Using AutoComplete with the Form
--------------------------------

Using this form the user has to manually enter the email address.
With AutoCompleteWidget we can suggest an email address when the
corresponding username is typed::

    from django import forms
    from autocomplete.widgets import AutoCompleteWidget

    class SendMail(froms.Form):
        to = forms.EmailField(widget=AutoCompleteWidget('emails',
                                                        force_selection=False))
        subject = forms.CharField(required=False)
        content = forms.CharField(widget=forms.Textarea)

The string ``'emails'`` passed as the first parameter of
:class:`~autocomplete.widgets.AutoCompleteWidget` is an
identifier used by autocomplete to select the correct choices-set to render.

``force_selection=False`` tells the Widget to not force the user to select one
of the displayed choices. We use this to allow the user to manually insert an
email address, without selecting a suggestion.

Defining the choices-set
------------------------

Now we have to register the ``emails`` choices-set editing our URLConf::

    from django.conf.urls.defaults import *
    from django.contrib.auth.models import User
    from autocomplete.views import autocomplete

    autocomplete.register(
        id = 'emails',
        queryset = User.objects.all(),
        fields = ('username', 'email'),
        limit = 5,
        key = 'email',
        label = 'email',
    )

.. note::

    Since we are using an EmailField in our Form we **must** set the *key*
    parameter to ``'email'``, otherwise the Form won't validate.

..
 In this way, when an user starts typing something (e.g. *bob*) all the
 email addresses that starts with that will be shown (e.g. *bob1@example.com* and
 *bob2@example.com*).
..
 But what happens if an user (e.g. *bob*) has an email address that doesn't start with
 his username (e.g. iam.bob@example.com) when you start typing his username?
..
 But the suggestion won't show up if you start typing an username (e.g. *bob*) which has an
 email address that doesn't match his username (e.g. *iam.bob@example.com*)

..
 But what if our user starts typing an username (e.g. *bob*) 
 But what if *Bob* has an email address like *foo@bobhost.com*? In this case his
 email address won't show up, because it doesn't start with *bob*. We can easily
 fix this by adding ``'username'`` to the fields of our choices-set.

In this way when the user starts typing either an username or an email address
a set of suggested email addresses will show up.

We'd also like to make the suggestion nicer, displaying the first and last name
of the user as well as the email address. We can do this using a formatter
function.

Our choices-set becomes::

    from django.conf.urls.defaults import *
    from django.contrib.auth.models import User
    from autocomplete.views import autocomplete

    def display_suggestion(user):
        return u"%s %s <%s>" % (user.first_name, user.last_name, user.email)

    autocomplete.register(
        id = 'emails',
        queryset = User.objects.all(),
        fields = ('username', 'email'),
        limit = 5,
        key = 'email',
        label = display_suggestion,
    )

Registering the autocomplete view
---------------------------------

Now edit your URLConf again and add the *autocomplete* view to your urls::

    urlpatterns = patterns('',
        # your other urls here.
        url('^autocomplete/(\w+)/$', autocomplete, name='autocomplete'),
    )

Ok. That's it. Just render the form in a template and enjoy.

.. seealso::

    :ref:`media-files-configuration`
        for how to configure and customize the
        Media files of your widget (including how to use `JQuery`_ or other js toolkits
        with Django AutoComplete).

.. _`JQuery`: http://jquery.com
