from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from autocomplete.views import AutocompleteSettings
from test_project.testapp.models import Dummy
from test_project.testapp.views import autocomplete

class SimpleAutocomplete(AutocompleteSettings):
    queryset = User.objects.all()
    search_fields = ('^username',)

class LoginRequiredAutocomplete(SimpleAutocomplete):
    login_required = True

class HasPermAutocomplete(SimpleAutocomplete):

    def has_permission(self, request):
        if request.user.has_perm('testapp.add_dummy'):
            return True
        return False

    def forbidden(self, request):
        ctx = {'settings': self, 'permission': 'testapp.add_dummy'}
        r = render_to_response('autocomplete/forbidden.html', ctx)
        r.status_code = 403
        return r


class CustomRenderingAutocomplete(SimpleAutocomplete):
    key = 'first_name'
    label = u'<em>%(email)s</em>'

    def value(self, u):
        return u.username.upper()

class LimitAutocomplete(SimpleAutocomplete):
    queryset = User.objects.filter(username__startswith='g').order_by('username')
    limit = 1

class User2Autocomplete(SimpleAutocomplete):
    queryset = None

class FriendsAutocomplete(AutocompleteSettings):
    search_fields = ('^username',)

class EmailAutocomplete(AutocompleteSettings):
    queryset = User.objects.all()
    search_fields = ('^email', '^username')
    key = value = 'email'

    def label(self, u):
        return u'%s %s \u003C%s\u003E' % (u.first_name, u.last_name, u.email)

autocomplete.register('testapp.simple', SimpleAutocomplete)
autocomplete.register('testapp.loginreq', LoginRequiredAutocomplete)
autocomplete.register('testapp.hasperm', HasPermAutocomplete)
autocomplete.register('testapp.customrender', CustomRenderingAutocomplete)
autocomplete.register(Dummy.user2, User2Autocomplete)
autocomplete.register('testapp.limit', LimitAutocomplete)
autocomplete.register(Dummy.friends, FriendsAutocomplete)
autocomplete.register('testapp.email', EmailAutocomplete)
