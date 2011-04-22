import locale
import unicodedata
import operator

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.db.models.fields.related import RelatedField



# Set locale (use for sorting in autocomplete)
# Simple solution but not really cool. We should avoid setting the locale in a web app.
if getattr(settings, 'LC_COLLATE', None) and locale.getlocale(locale.LC_COLLATE) == (None, None):
    locale.setlocale(locale.LC_COLLATE, settings.LC_COLLATE)


def strip_accents(text):
    """
    Remove accents (diacritic) from all characters.
    """
    return ''.join((char for char
                    in unicodedata.normalize('NFD', text)
                    if not unicodedata.combining(char)))


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
    lookup = True
    add_button = True
    reverse_label = None
    login_required = False
    js_options = {}

    # Javascript settings
    delimiter = u''
    auto_focus = True
    min_length = 1
    highlight = True
    zebra = True
    cache = True

    def label(self, obj):
        return unicode(obj)
    value = label


    def __init__(self, id, current_app, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)
        # Set JS options from class attributes (and indirectly from kwargs).
        self.js_options = {
                     'delimiter': self.delimiter,
                     'autoFocus': self.auto_focus,
                     'minLength': self.min_length,
                     'highlight': self.highlight,
                     'zebra': self.zebra,
                     'cache': self.cache
                     }

        self.id = id
        self.current_app = current_app

        if isinstance(id, RelatedField):
            self.field = id
            self.model = self.field.rel.to
            opts = self.field.related.opts
            self.id = '.'.join((opts.app_label, opts.module_name,
                self.field.name))
            if self.queryset is None:
                self.queryset = self.model._default_manager.complex_filter(
                    self.field.rel.limit_choices_to)
            if self.key is None:
                self.key = self.field.rel.get_related_field().name
            if self.reverse_label is None:
                self.reverse_label = True
        elif isinstance(id, (str, unicode)):
            self.field = None
            self.model = self.queryset.model
            self.id = id
            if self.key is None:
                self.key = 'pk'
            if self.reverse_label is None:
                self.reverse_label = False
        else:
            raise TypeError("id should be either a related field or a string: %r" % id)
        self.path = self.id.replace('.', '/')

        def build_func(attr):
            if attr in self.model._meta.get_all_field_names():
                return lambda m: getattr(m, attr)
            return lambda m: attr % vars(m)

        for name in ('value', 'label'):
            attr = getattr(self, name)
            if isinstance(attr, (str, unicode)):
                setattr(self, name, build_func(attr))

    def view(self, request):
        if not self.has_permission(request):
            return self.forbidden(request)

        query = request.GET.get('term', None)

        if query is None:
            query = request.GET.get('lookup', None)
            
            if query is None:
                raise Http404
            
            # lookup query
            try:
                data = smart_str(self.queryset.get(pk=query))
            except ObjectDoesNotExist:
                data = u''

        elif self.delimiter:
            # query for a multi-term field
            delimiter = u'%s ' % self.delimiter
            query = strip_accents(query.lower())
            results = set()
            for field_name in self.search_fields:
                field_name = smart_str(field_name)
                if field_name[0] in '^=@':
                    real_field_name = field_name[1:]
                else:
                    real_field_name = field_name
                
                # get results from rows without delimiter
                queryset = self.queryset.exclude(**{'%s__icontains' % real_field_name: delimiter})
                queryset = queryset.filter(**{self._construct_search(field_name): query})
                queryset = queryset.values_list(real_field_name, flat=True).distinct()
                results.update(queryset[:self.limit])
                
                # get results from rows with delimiter
                queryset = self.queryset.filter(**{'%s__icontains' % real_field_name: delimiter})
                queryset = queryset.filter(**{'%s__icontains' % real_field_name: query})
                queryset = queryset.values_list(real_field_name, flat=True).distinct()
                
                def test(value):
                    value = strip_accents(value.lower())
                    if field_name.startswith('^'):
                        return value.startswith(query)
                    elif field_name.startswith('='):
                        return value == query
                    else:
                        return query in value
                
                for values in queryset[:self.limit]:
                    results.update((value for value in values.split(delimiter) if test(value)))
                            
            data = []
            results = list(results)
            results.sort(cmp=locale.strcoll)
            for o in list(results)[:self.limit]:
                data.append({
                             'id': len(data),
                             'value': o,
                             'label': o
                             })

        else:
            # normal query
            queryset = self.queryset
            for bit in query.split():
                or_queries = [models.Q(**{self._construct_search(
                    smart_str(field_name)): bit})
                        for field_name in self.search_fields]
    
                queryset = queryset.filter(reduce(operator.or_, or_queries))
    
            data = []
            for o in queryset[:self.limit]:
                data.append(dict(
                    id=getattr(o, self.key),
                    value=self.value(o),
                    label=self.label(o),
                ))

        return HttpResponse(simplejson.dumps(data), mimetype='application/json')

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
        if self.login_required:
            return request.user.is_authenticated()
        return True

    def forbidden(self, request):
        return HttpResponseForbidden()

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
            id = self.settings[id].id
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

autocomplete = AutocompleteView()
