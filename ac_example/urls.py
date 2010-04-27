from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.models import User

from autocomplete.views import autocomplete


autocomplete.register(
    id = 'user', 
    queryset = User.objects.all(),
    fields = ('username', 'email'),
    limit = 5,
)

autocomplete.register(
    id = 'name',
    queryset = User.objects.all(),
    fields = ('first_name',),
    limit = 5,
    key = 'username',
    label = 'username',
)

urlpatterns = patterns('',
    # If you want to use the same AutoComplete instance as a view for multiple
    # applications, you should register it only once in your project's URLconf.
    url('^autocomplete/(\w+)/$', autocomplete, name='autocomplete'),
    url('^example/$', 'ac_example.views.example'),
)

# Remember to serve the files in autocomplete/media from your MEDIA_URL.
# When DEBUG is True you can accomplish this by using the builtin django's
# "static.serve" view. XXX Make sure that MEDIA_URL in your settings.py is
# pointing to this view (i.e. "http://localhost:8000/site_media/").
if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^site_media/(?P<path>.*)$', 'serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
