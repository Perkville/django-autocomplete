Features
========

- Uses `jQuery UI Autocomplete`_.
- ForeignKey and ManyToManyField completition.
- Completition for CharField, IntegerField and hopefully any Field.
- Easy Admin integration.

.. _`jQuery UI Autocomplete`: http://jqueryui.com/demos/autocomplete/

Usage Example
=============

Make the files under ``autocomplete/media`` accessible from
``settings.AUTOCOMPLETE_MEDIA_PREFIX`` (You can accomplish this by either
linking or copying ``autocomplete/media`` in your project's media dir)::
    AUTOCOMPLETE_MEDIA_PREFIX = '/path/to/autocomplete/media/'

Include the view in your project's URLConf::
    import autocomplete
    
    url('^autocomplete/', include(autocomplete.view.urls))

Register a couple of ``AutocompleteSettings`` objects and start using them (for
example in admin.py)::
    from django.contrib import admin
    from django.contrib.auth.models import Message
    
    import autocomplete
    
    class UserAutocomplete(autocomplete.AutocompleteSettings):
        search_fields = ('^username', '^email')
    
    autocomplete.view.register(Message.user, UserAutocomplete)
    
    class MessageAdmin(autocomplete.AutocompleteAdmin, admin.ModelAdmin):
        pass
    
    admin.site.register(Message, MessageAdmin)




