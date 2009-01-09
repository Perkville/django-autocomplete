from django.conf.urls.defaults import *

from django.contrib.auth.models import User
from autocomplete.views import autocomplete


autocomplete.register('user', User.objects.all(), ('username', 'email'), 5)

urlpatterns = patterns('',
    url('^autocomplete/(\w+)/$', autocomplete, name='autocomplete'),
    url('^example/$', 'ac_example.views.example'),
)
