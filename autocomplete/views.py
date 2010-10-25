import operator

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.contrib.admin.validation import check_isseq
from django.db import models
from django.http import Http404, HttpResponse
from django.utils import simplejson
from django.utils.encoding import smart_str


class AlreadyRegistered(Exception):
    pass


class AutocompleteSettings(object):
    """
    >>> class MySettings(AutocompleteSettings):
    ...     pass
    """
    queryset = key = None
    search_fields = []
    limit = 5
    reverse_label = None
    js_options = {}
 
    def label(self, obj):
        return unicode(obj)
    value = label
   

    def __init__(self, id, current_app, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)
        self.id = id
        self.current_app = current_app

        if isinstance(id, models.Field):
            self.field = id
            self.model = self.field.rel.to
            opts = self.field.model._meta
            self.path = '/'.join((opts.app_label, opts.module_name,
                self.field.name))
            if self.queryset is None:
                self.queryset = self.model._default_manager.complex_filter(
                    self.field.rel.limit_choices_to)
            if self.key is None:
                self.key = self.field.rel.get_related_field().name
            if self.reverse_label is None:
                self.reverse_label = True
        else:
            self.field = None
            self.model = self.queryset.model
            self.path = id.replace('.', '/')
            if self.key is None:
                self.key = 'pk'
            if self.reverse_label is None:
                self.reverse_label = False

        def build_func(attr):
            if attr in self.model._meta.get_all_field_names():
                 return lambda m: getattr(m, attr)
            return lambda m: value % vars(m)

        for name in ('value', 'label'):
            attr = getattr(self, name)
            if isinstance(attr, (str, unicode)):
                setattr(self, name, build_func(attr))

    def view(self, request):
        query = request.GET.get('term', None)

        if query is None:
            return self.not_found(request)

        if not self.has_permission(request):
            return self.forbidden(request)

        queryset = self.queryset
        for bit in query.split():
            or_queries = [models.Q(**{self._construct_search(
                smart_str(field_name)): bit})
                    for field_name in self.search_fields]

            queryset = queryset.filter(reduce(operator.or_, or_queries))
        
        data = []
        for o in queryset[:self.limit]:
            data.append(dict(
                id = getattr(o, self.key),
                value = self.value(o),
                label = self.label(o),
            ))
        
        # XXX set the mimetype
        return HttpResponse(simplejson.dumps(data))

    def _construct_search(self, field_name):
        # use different lookup methods depending on the notation
        if field_name.startswith('^'):
            return "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            return "%s__search" % field_name[1:]
        else:
            return "%s__icontains" % field_name

    def has_permission(self, request):
        return True

    def forbidden(self, request):
        return HttpResponseForbidden()

    def not_found(self, request):
        raise Http404

    def get_absolute_url(self):
        return reverse('autocomplete:autocomplete', args=[
            self.path], current_app=self.current_app)


class AutocompleteView(object):
    """
    >>> from django.contrib.auth.models import User
    >>> autocomplete = AutocompleteView()

    >>> class UserAutocomplete(AutocompleteSettings):
    ...     queryset = User.objects.all()
    ...     search_fields = ('^username', 'email')
    ... 
    >>> autocomplete.register('myapp.user', UserAutocomplete)
    >>> autocomplete.get_settings(Message.user)
    >>> autocomplete.has_settings('myapp.user')
    """

    def __init__(self, name='autocomplete', app_name='autocomplete'):
        self.settings = {}
        self.paths = {}
        self.name = name
        self.app_name = app_name

    def has_settings(self, id):
        return getattr(id, 'field', id) in self.settings

    def get_settings(self, id):
        return self.settings[getattr(id, 'field', id)]

    def register(self, id, settings_class=AutocompleteSettings, **options):
        id = getattr(id, 'field', id)
        if id in self.settings:
            id = self.settings.path.replace('/', '.')
            raise AlreadyRegistered('%r is already registered' % id)

        self.settings[id] = settings = settings_class(id, self.name, **options)
        self.paths[settings.path] = settings

    def __call__(self, request, path):
        if path not in self.paths:
            raise Http404

        return self.paths[path].view(request)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('',
            url(r'(.+)/$', self, name='autocomplete'))
        return urlpatterns

    def urls(self):
        return self.get_urls(), self.app_name, self.name
    urls = property(urls)

view = AutocompleteView()
