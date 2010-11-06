from django.conf.urls.defaults import *
from test_project.testapp import views

import test_project.testapp.autocomplete_settings

urlpatterns = patterns('',
    url('^autocomplete/', include(views.autocomplete.urls)),
)
