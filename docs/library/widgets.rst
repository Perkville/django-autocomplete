:mod:`autocomplete.widgets` AutoCompleteWidget
==============================================

.. module:: autocomplete.widgets

.. class:: AutoCompleteWidget(ac_name[, force_selection[, reverse_label[, view[, attrs]]]])

    Just as a Select widget an
    :class:`AutoCompleteWidget` lets the user select a *choice*
    from a dropdown box but
    Instead of displaying all the choices at once, the
    :class:`AutoCompleteWidget` requires
    the user to start typing some characters and then gathers, using javascript,
    the choices matching the user input from a remote :class:`~autocomplete.views.AutoCompleteView`.
    
    Performing smaller queries, instead of a single enormous one to get all the
    choices at once, significantly reduces the load of the database. Moreover
    it makes easier to select the right choice, because the user has not to search
    among a big number of options like it could happen with a Select widget.

    To make an :class:`AutoCompleteWidget` work you need to:
     * serve the javascript that will render the choices to the user;
     * add an :class:`~autocomplete.views.AutoCompleteView` to your URLConf so
       the javascript can collect the choices to display;
     * define one or more *choices-sets* for the
       :class:`~autocomplete.views.AutoCompleteView` to render.

    .. note::
        
        To handle relationships between models use
        :class:`autocomplete.fields.ModelChoiceField`.
        It is just like a normal ModelChoiceField but uses an
        :class:`AutoCompleteWidget` (by default) to render its choices.


    .. data:: AC_TEMPLATE

        A string representing the template that
        :class:`AutoCompleteWidget` uses to render itself as html.
        It will be formatted with a dict containing the following
        keys: ``name``, ``hidden_value``, ``value``, ``url`` and ``force_selection``.


    .. method:: __init__(ac_name[, force_selection[, reverse_label[, view[, attrs]]]])
        
        *ac_name*
            The name of the choices-set to use with this instance of
            :class:`AutoCompleteWidget`.

        *force_selection*
            If is set to True forces the user to select a valid choice. If left
            to False lets the user write anything in the input.
            When using :class:`~autocomplete.fields.ModelChoiceField` it is
            automatically set to True, to ensure a valid model is selected.
            You should set it to False when you want to provide suggestions to
            the user.

        *reverse_label*
            Whether to obtain the label of a choice from its key when rendering
            the widget with an initial value, or not. This is always set to
            True by default.

        *view*
            The view used to retrieve the choices, defaults to
            :obj:`autocomplete.views.autocomplete`.

        *attrs*
            A set of html attributes to insert in the autocomplete
            input field, to customize it (e.g. to add css classes).


    .. method:: render(name, value[, attrs])
        
        Method used to render the widget as html.

        If the Form is being edited *value* is set to the key of one of the
        choices (and will be reversed if reverse_label is True), otherwise it
        is set to None.

        *attrs*
            A set of html attributes to insert in the autocomplete
            input field, to customize it (e.g. to add css classes).


.. data:: AC_TEMPLATE

    The default template used by
    :class:`AutoCompleteWidget` to
    render itself.


.. _media-files-configuration:

Configuring the Media files of :class:`AutoCompleteWidget`
----------------------------------------------------------

By default the :class:`AutoCompleteWidget` uses YUI served from http://yahooapis.com in
conjunction with the ``js/yui_autocomplete.js`` provided in this package. This
to not include directly YUI in Django AutoComplete, and to provide a quickly working
setup. This solution, assuming you are serving ``js/yui_autocomplete.js`` from
your ``MEDIA_URL``, should work in every situation, including the admin
application. However in some cases you could need to customize the Media files
of the widget. For example, if you are already using YUI in your template and
you don't want it to be included twice, or if you wish to use JQuery or any
other javascript toolkit [1]_.

::

    AutoCompleteWidget(your_params)
    # uses YUI loaded from http://yahooapis.com and js/yui_autocomplete.js

    class CustomYUIACWidget(AutoCompleteWidget):
        """
        This widget uses your version of YUI served directly from your
        MEDIA_URL.
        """
        class Media:
            extend = False
            js = ('js/path/to/yui.js',
                  # ...
                  # ...
                  'js/yui_autocomplete.js')


    class CustomJQueryACWidget(AutoCompleteWidget):
        """
        This widget uses JQuery served from MEDIA_URL.
        """
        class Media:
            extend = False
            css = {'all': ('js/thickbox.css',)}
            js = ('js/jquery.min.js',
                'js/jquery.bigframe.min.js',
                'js/jquery.ajaxQueue.js',
                'js/thickbox-compressed.js',
                'js/jquery.autocomplete.min.js',
                'js/jquery_autocomplete.js')


    class AnyOtherToolkitACWidget(AutoCompleteWidget):
        class Media:
            extend = False
            js = ('js/path/to/your/toolkit.js',
                  # ...
                  # ...
                  'yourtoolkit_autocomplete.js')

.. note::

    Remember to set ``extend = False`` in your subclass' Media, otherwise your
    files will be *added* to the default ones instead of replacing them.

.. seealso::
    
    `Static Files <http://docs.djangoproject.com/en/dev/howto/static-files/>`_
        How to correctly serve static files.

    `Form Media <http://docs.djangoproject.com/en/dev/topics/forms/media/>`_
        How to customize the CSS and Javascript resources of a Form.


.. rubric:: Footnotes

.. [1] Currently this package provides only ``yui_autocomplete.js`` and 
       ``jquery_autocomplete.js``. If you want to use an other toolkit you will
       have to make the script yourself.

