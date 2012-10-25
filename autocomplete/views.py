import unicodedata
import operator

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.db.models.fields.related import RelatedField



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
    distinct = False
    lookup = True
    add_button = True
    reverse_label = None
    login_required = False
    sort_cmp = None    
    sort_key = None
    js_options = {}

    # Javascript settings
    delimiter = u''
    delimiter_list = True
    auto_focus = True
    min_length = 1
    highlight = True
    zebra = True
    cache = True

    def _label(self, obj):
        return unicode(obj)
    value = _label
    label = _label


    def __init__(self, id, current_app, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)
        # Set JS options from class attributes (and indirectly from kwargs).
        self.js_options = {
                     'delimiter': self.delimiter,
                     'delimiterList': self.delimiter_list,
                     'autoFocus': self.auto_focus,
                     'minLength': self.min_length,
                     'highlight': self.highlight,
                     'zebra': self.zebra,
                     'cache': self.cache
                     }

        if isinstance(self.queryset, models.base.ModelBase):
            self.queryset = self.queryset._default_manager.all()
        if isinstance(self.search_fields, basestring):
            self.search_fields = (self.search_fields,)


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
        elif isinstance(id, models.Field):
            self.field = id
            self.model = id.model
            self.id = '.'.join((id.model.__name__, id.name))
            if not self.search_fields:
                self.search_fields = [id.name]
            if self.queryset is None:
                self.queryset = id.model._default_manager.all()
            if self.value == self._label:
                self.value = id.name
            if self.label == self._label:
                self.label = id.name
            if self.key is None:
                self.key = 'pk'
            if self.reverse_label is None:
                self.reverse_label = False
        elif isinstance(id, basestring):
            self.field = None
            self.model = self.queryset.model
            self.id = id
            _, value = id.split(u'.')
            if not self.search_fields:
                self.search_fields = (value,)
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

        else:
            data = self.sub_view(query)
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')
            
    def sub_view(self, query):
        data = []

        if self.delimiter and not isinstance(self.field, RelatedField):
            # query for a Delimited field
            query = strip_accents(query.lower())
            
            start_results = set()
            contains_results = set()
            
            for field_name in self.search_fields:
                limit = self.limit
                field_name = smart_str(field_name)
                if field_name.startswith('^'):
                    field_name = field_name[1:]
                    contains = False
                else:
                    contains = True
                    
                start_subresults = set()
                contains_subresults = set()
                
                contains_query = models.Q(**{'%s__icontains' % field_name: query})
                
                # get results from rows without delimiter
                delimiter_query = models.Q(**{'%s__icontains' % field_name: self.delimiter})
                queryset = self.queryset.exclude(delimiter_query)
                queryset = queryset.filter(**{'%s__istartswith' % field_name: query})
                queryset = queryset.values_list(field_name, flat=True).distinct().order_by(field_name)
                start_subresults.update(queryset[:limit])
                
                # get results from rows with delimiter
                delimiter_queryset = self.queryset.filter(delimiter_query).filter(contains_query)
                delimiter_queryset = delimiter_queryset.values_list(field_name, flat=True).distinct()
            
                limit = max((limit + 1) / 2, limit - len(start_subresults))

                for values in delimiter_queryset[:limit]:
                    start_subresults.update((value
                                             for value
                                             in values.split(self.delimiter)
                                             if strip_accents(value.lower()).startswith(query)))
    
                start_results.update(start_subresults)

                limit = self.limit - len(start_subresults)

                if contains and limit > 0:
                    # get results from rows without delimiter
                    queryset = self.queryset.exclude(delimiter_query)
                    queryset = queryset.filter(contains_query)
                    queryset = queryset.values_list(field_name, flat=True).distinct().order_by(field_name)
                    contains_subresults.update(queryset[:limit])
                    
                    limit = max((limit + 1) / 2, limit - len(contains_subresults))
                                        
                    for values in delimiter_queryset[:limit]:
                        contains_subresults.update((value
                                                    for value
                                                    in values.split(self.delimiter)
                                                    if query in strip_accents(value.lower())))
                        
                    contains_results.update(contains_subresults)
                    
            contains_results.difference_update(start_results)
            contains_results = list(contains_results)
            contains_results.sort(cmp=self.sort_cmp, key=self.sort_key)
            start_results = list(start_results)
            start_results.sort(cmp=self.sort_cmp, key=self.sort_key)
            start_results.extend(contains_results)
                            
            for o in start_results[:self.limit]:
                data.append({
                             'id': len(data),
                             'value': o,
                             'label': o
                             })

        elif isinstance(self.field, models.CharField):
            # Query distinct text in a CharField
            queryset = self.queryset.distinct()
            results = []
            contains = []
            start_queries = []
            contains_queries = []
            
            for field_name in self.search_fields:
                limit = self.limit - len(start_queries)
                if limit <= 0:
                    break
                field_name = smart_str(field_name)
                if field_name.startswith('^'):
                    field_name = field_name[1:]
                else:
                    contains.append(field_name)
                # Remove '-' character showing order
                order = field_name
                field_name = field_name.lstrip('-')
                    
                start_query = queryset.exclude(
                                    **{'%s__in' % field_name: start_queries}
                                ).filter(
                                    **{'%s__istartswith' % field_name: query}
                                ).values_list(
                                    field_name, flat=True
                                ).order_by(order)
                start_queries.extend(start_query[:limit])
                
            results.extend(sorted(start_queries, cmp=self.sort_cmp, key=self.sort_key))

            for field_name in contains:
                limit = self.limit - len(results) - len(contains_queries)
                if limit <= 0:
                    break
                order = field_name
                field_name = field_name.lstrip('-')
                    
                contains_query = queryset.exclude(
                                    **{'%s__in' % field_name: results + contains_queries}
                                ).filter(
                                    **{'%s__icontains' % field_name: query}
                                ).values_list(
                                    field_name, flat=True
                                ).order_by(order)
                contains_queries.extend(contains_query[:limit])

            results.extend(sorted(contains_queries, cmp=self.sort_cmp, key=self.sort_key))

            for idx, value in enumerate(results):
                data.append(dict(
                    id=idx,
                    value=value,
                    label=value,
                ))

        else:
            # Normal query
            results = []
            start_queries = []
            contains_queries = []
            
            if self.distinct:
                limit_pow = 2
            else:
                limit_pow = 1

            for field_name in self.search_fields:
                field_name = smart_str(field_name)
                # Dropping support for '@' and '=' search type.
                # '@' works only with MySQL MyISAM tables, and only when correctly set.
                # Most of the time with Django and MySQL, INNODB is use.
                # I can't see a use case for '=' in an autocomplete field?
                if field_name.startswith('^'):
                    field_name = field_name[1:]
                    contains = False
                else:
                    contains = True
                # Remove '-' character showing order
                field_name = field_name.lstrip('-')
                    
                start_queries.append(models.Q(**{'%s__istartswith' % field_name: query}))

                if contains:
                    contains_queries.append(models.Q(**{'%s__icontains' % field_name: query}))

            queryset = self.queryset.order_by(*[field_name.lstrip('^') for field_name in self.search_fields])
            start_query = queryset.filter(reduce(operator.or_, start_queries))
            results.extend(start_query[:self.limit ** limit_pow])

            limit = self.limit - len(results)
            if contains_queries and limit > 0:
                contains_query = queryset.exclude(pk__in=start_query).filter(reduce(operator.or_, contains_queries))
                results.extend(contains_query[:limit ** limit_pow])

            values = []
            for o in results:
                value = self.value(o)
                if not self.distinct or value not in values:
                        values.append(value)
                        data.append(dict(
                            id=getattr(o, self.key),
                            value=value,
                            label=self.label(o),
                        ))
                        if self.distinct and len(values) >= self.limit:
                            break
        return data

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
            url(r'(.+)/$', self, name='autocomplete', kwargs={'SSL': True}))
        return urlpatterns

    def urls(self):
        return self.get_urls(), self.app_name, self.name
    urls = property(urls)

autocomplete = AutocompleteView()
