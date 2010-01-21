:mod:`autocomplete.fields` ModelChoiceField
===========================================

.. module:: autocomplete.fields

.. _modelchoicefield:

.. class:: ModelChoiceField(ac_name[, reverse_label[, view[, widget[, **kwargs]]]])

    A form field similar to ``django.forms.ModelChoiceField``, which uses
    an :class:`~autocomplete.widgets.AutoCompleteWidget` instead of a
    ``forms.Select`` to render its choices.
    If you do not specify a widget, :class:`ModelChoiceField` will instantiate
    a new :class:`~autocomplete.widgets.AutoCompleteWidget` with the
    ``ac_name`` and ``reverse_label`` parameters you provided.
    If you want to use a customized version of
    :class:`~autocomplete.widgets.AutoCompleteWidget` you must pass an
    instance::
        
        ModelChoiceField('myac', widget=MyACWidget('myac', **custom_params))


    *ac_name*
        The id of a choice-set previously registered with the *view*.
    
    *reverse_label*
        Whether to obtain the label of a choice from its key when rendering
        the widget with an initial value, or not. This is always set to
        True by default.

    *view*
        the view used to retrieve the choices, defaults to
        :obj:`autocomplete.views.autocomplete`.

    *widget*
        the widget to use, defaults to
        :class:`autocomplete.widgets.AutoCompleteWidget`.

    *\*\*kwargs*
        other keyword arguments that are passed to the Django's Widget.__init__
        method.



