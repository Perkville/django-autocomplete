from django.conf.urls.defaults import *

from django.contrib.auth.models import User
from autocomplete.views import autocomplete


autocomplete.register('user', User.objects.all(), ('username', 'email'), 5)
autocomplete.register('name', User.objects.all(), ('username',), 5, 'username', 'username')

urlpatterns = patterns('',
    url('^autocomplete/(\w+)/$', autocomplete, name='autocomplete'),
    url('^example/$', 'ac_example.views.example'),
)
