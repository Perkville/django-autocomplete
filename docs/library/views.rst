:mod:`autocomplete.views` AutoComplete Views
============================================

.. module:: autocomplete.views


.. class:: AutoCompleteView

    The AutoCompleteView is called by an Ajax request when the user starts typing
    [#]_ and returns a set of options, matching the user input, for the requested
    choices-set. The output is encoded as JSON (``mimetype='application/json'``) and
    consists of a list of *key-label* pairs::

        # Request:
        GET /autocomplete/fruit/?query=red
        
        # JSON Response:
        [[9, "Strawberry"], [10, "Cherry"], [11, "Apple"]]

    Since the AutoCompleteView is a class you can subclass it to customize its
    behaviour. However a simple instance (:obj:`autocomplete.views.autocomplete`)
    is made available, and it's used for the default value of the *view* argument in
    :class:`~autocomplete.widgets.AutoCompleteWidget` and
    :class:`~autocomplete.fields.ModelChoiceField`.

    .. data:: settings

        A ``dict`` containing the configuration of all the choices-sets
        registered.


    .. method:: __call__(request, ac_name[, query_param])
        
        This method makes AutoCompleteView's instances callable and thus usable
        as views.

        The optional argument *query_param* is the name of the GET parameter
        that should contain the user input. It defaults to ``'query'``.

        If the Javascript toolkit you're using requires you to use an other
        value (e.g. ``'q'``) you can customize this param, by passing a
        ``dict`` to the autocomplete view in your URLConf::

            url('^autocomplete/(\w+)$', autocomplete, dict(query_param='q')),


    .. method:: not_found(request, ac_name):
        
        Called when an user asks for an inexisting choices-set.
        It must return an HttpResponse object for the client.


    .. method:: forbidden(request, ac_name):
        
        Called when an user is not authorized to access a choices-set.
        This means that the user is not authenticated and ``auth=True`` has
        been set in the choices-set.
        It must return an HttpResponse object for the client.

    .. method:: reverse_label(ac_name, key_value)

        Method used to obtain the label from its corresponding key.
        This is mostly used when rendering forms with an *initial* value for an
        AutoCompleteWidget.


    .. method:: register(id, queryset, fields[, limit[, key[, label[, auth]]]])
        
        This method is used to register a new choices-set with this instance of
        AutoCompleteView.

        The method accepts as paramter:

         *id*
            a sequence of letters [#]_ that identifies the choices-set.

         *queryset*
            the queryset that contains all the possible choices.

            .. note::
                
                AutoCompleteView is only able to work with querysets and not with
                normal *hardcoded* choices, as widgets.Select does.

         *fields*
            A tuple of field names used to construct the query to get the choices
            matching the given user input. if ``'__'`` is not present in a field
            ``'__startswith'`` will be appended to it.
            
            ::

                fields = ('username', 'email__exact')
                # becomes:
                Q(username__startswith=user_input) | Q(email__exact=user_input)

         *limit*
            A positive integer used to limit the result of the query.

         *key*
            A field name, by default ``'pk'``, needed to identify the choices in the
            queryset. It **must** be an unique field, otherwise more than one choice
            could have the same key.

         *label*
            Can be an existing field of the queryset's model or a function that accepts
            a model as its unique argument and returns a string representation of that
            model. By default it is::
                
                label = lambda obj: smart_unicode(obj)

            .. note::
                
                Using a function means that the view will have to get from the db the
                entire model with all its fields (``SELECT * FROM Model``). Using a
                field instead will select only the given field.

         *auth*
            When set to ``True`` only authenticated users will be able to access this
            choices-set. Defaults to ``False``.

.. data:: autocomplete

    This is the AutoCompleteView used by default. It's an instance of
    :class:`~autocomplete.views.AutoCompleteView`. If you want to customize
    your AutoComplete view, you should subclass
    :class:`autocomplete.views.AutoCompleteView`.


Using the autocomplete view in your URLConf
-------------------------------------------

Here's an example of how to edit
your URLConf to use the default AutoCompleteView's instance::

    # your project's urls.py
    from django.conf.urls.defaults import *
    from autocomplete.views import autocomplete

    urlpatterns = patterns('',
        # your other urls here.
        url(r'^autocomplete/(\w+)/$', autocomplete),
    )

Customizing the AutoCompleteView
--------------------------------

The methods that can be overidden
are ``not_found`` and ``forbidden``. They are called respectively when the requested
choices-set does not exist and when the request is not allowed to access the
choices-set. Both these methods should return a HttpResponse object.

::

    from django.http import HttpResponse
    from autocomplete.views import AutoCompleteView

    class MyACView(AutoCompleteView):

        def not_found(self, request, ac_name):
            content = "choices-set %s, not found" % (ac_name,)
            return HttpResponse(content, status=404)

        def forbidden(self, request, ac_name):
            content = "login to access this choices-set"
            return HttpResponse(content, status=403)

    myacview = MyACView()

You URLConf becomes::

    # your project's urls.py
    from django.conf.urls.defaults import *
    
    from myapp.views import myacview

    urlpatterns = patterns('',
        # your other urls here.
        url(r'^autocomplete/(\w+)/$', myappview),
    )


.. note::

    Remember that if you use a custom view you have to explicitly pass it to
    your AutoCompleteWidget(s) and ModelChoiceField(s) through the ``view``
    argument.


.. rubric:: Footnotes

.. [#] By default everytime the user types a character a call is made. See your
       Javascript toolkit's Documentation if you want to change this behaviour.

.. [#] You can use any characters you want until they match the autocomplete
       view's regexp in your URLConf.

