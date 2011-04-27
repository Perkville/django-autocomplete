Features
========

- Uses `jQuery UI Autocomplete`_.
- ForeignKey and ManyToManyField completition.
- Completition for CharField, IntegerField and hopefully any Field.
- Easy Admin integration.

.. _`jQuery UI Autocomplete`: http://jqueryui.com/demos/autocomplete/

Added Features in this version
==============================

New options for the autocomplete widget:

    - Highlight (put in bold the search term in the results list)
    - Auto Focus (automatically select the first result of the list)
      need jQuery UI >= 1.8.11
    - Zebra (colorize list rows in alternance)
    - Simple Cache (cache each different query)
    - Add button (the green plus to add a new item for a Relation Field)
    - Lookup button (the loupe like in a RawIdField to select from the complete list)
    - Multiterms (possibility to have completion on many terms in one field
      separated by a delimiter, for example: a tag field)
    - Distinct result (get only distinct results for all fields excepted Relation fields)
  
All theses options can be set in the AutocompleteSettings class like this::

    class MyAutocompleteSettings(AutocompleteSettings):
        highlight = True
        auto_focus = True
        zebra = True
        cache = True
        add_button = True
        lookup = True
        delimiter = ','
        distinct = True

Or in the register function like this::

    autocomplete.register(  Message.user,
                            UserAutocomplete,
                            highlight=True,
                            auto_focus=True,
                            zebra=True,
                            cache=True,
                            add_button=True,
                            lookup=True,
                            delimiter=',',
                            distinct=True)

Visual changes:

    - Widget look that merge better with Django Admin.
    - Many to many list look that merge better with Django Admin.
    - Added a spinner (throbber) in the field when waiting for a request result.
    - Added support to show the help text in the admin.
    - Added possibility to override the many to many fields default help text.

Results sorting:

    - Fields with *contains* query will show in first the results that start by the query.

Admin Shortcuts:

    - Settings Auto registering.
    - Auto QuerySet
    - Auto search fields
    - Auto tuple (put single field automatically in a tuple)
    - Auto value and label from ID

All theses shortcuts give you the possibility to define all your autocomplete
fields in the Admin like this::

    MyClassAdmin(models.Admin):
        autocomplete_fields = {
                                'title': {},
                                'name': {'distinct': True},
                                'aforeignkeyfield': {'search_fields': '^text',
                                                     'add_button': False,
                                                     'lookup': True},
                                'am2mfield': {'search_fields': ('big', '^small')}
                                }
                                
No need to register or to create an AutocompleteSettings class.
The *title* CharField will have theses attributes automatically set:

    - search_fields = ('title',)
    - value = label = 'title'
    - queryset = MyClass._default_manager.all()

Usage Example
=============

Make the files under ``autocomplete/media`` accessible from
``settings.AUTOCOMPLETE_MEDIA_PREFIX`` (You can accomplish this by either
linking or copying ``autocomplete/media`` in your project's media dir)::

    AUTOCOMPLETE_MEDIA_PREFIX = '/path/to/autocomplete/media/'

Include the view in your project's URLConf::

    from autocomplete.views import autocomplete
    
    url('^autocomplete/', include(autocomplete.urls))

Register a couple of ``AutocompleteSettings`` objects and start using them (for
example in admin.py)::

    from django.contrib import admin
    from django.contrib.auth.models import Message
    
    from autocomplete.views import autocomplete, AutocompleteSettings
    from autocomplete.admin import AutocompleteAdmin
    
    class UserAutocomplete(AutocompleteSettings):
        search_fields = ('^username', '^email')
    
    autocomplete.register(Message.user, UserAutocomplete)
    
    class MessageAdmin(AutocompleteAdmin, admin.ModelAdmin):
        pass
    
    admin.site.register(Message, MessageAdmin)


