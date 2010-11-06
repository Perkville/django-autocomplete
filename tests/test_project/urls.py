import os
from django.conf import settings
from django.conf.urls.defaults import *
# from django.contrib import admin

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^testapp/', include('test_project.testapp.urls')),
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    import autocomplete
    urlpatterns += patterns('',
            url(r'^%s(?P<path>.*)$' % settings.AUTOCOMPLETE_MEDIA_PREFIX[1:],
            'django.views.static.serve',
            {'document_root': os.path.join(autocomplete.__path__[0], 'media')})
    )
