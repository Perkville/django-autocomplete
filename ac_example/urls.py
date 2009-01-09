from django.conf.urls.defaults import *

from django.contrib.auth.models import User
from autocomplete import ac

info_dict = {
    'settings': {
        'user': ac(User.objects.all(), ('username', 'email'), 5),
    },
    'query_param': 'query',
}

urlpatterns = patterns('',
    url('^autocomplete/(\w+)/$', 'autocomplete.views.autocomplete', info_dict,
        name='autocomplete'),
    url('^example/$', 'actest.acapp.views.example'),
)
