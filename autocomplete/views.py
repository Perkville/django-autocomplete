from django.http import HttpResponse
from django.db.models import Q
from django.utils import simplejson
from django.utils.encoding import smart_unicode

AUTOCOMPLETE_NOTFOUND = HttpResponse(status=404)
AUTOCOMPLETE_FORBIDDEN = HttpResponse(status=403)

class AutoComplete(object):

    def __init__(self):
        self.settings = dict()

    def __call__(self, request, ac_name, query_param='query'):
        if not self.settings.get(ac_name):
            return AUTOCOMPLETE_NOTFOUND

        qs, fields, limit, key, label, auth = self.settings[ac_name]
        if auth and not request.user.is_authenticated():
            return AUTOCOMPLETE_FORBIDDEN
        query = request.GET.get(query_param, '')
        
        filter = Q()
        for field in fields:
            if not '__' in field:
                field = '%s__startswith' % field
            filter |= Q(**{field: query})
        
        qs = qs.filter(filter)[:limit]
        
        if isinstance(label, basestring):
            if key == 'pk':
                key = qs.model._meta.pk.attname
            result = list(qs.values_list(key, label))
        else:
            result = []
            for obj in qs:
                result.append((getattr(obj, key), label(obj)))
        return HttpResponse(simplejson.dumps(result),
                mimetype='application/json')

    def register(self, id, queryset, fields, limit=None, key='pk', label=lambda obj: smart_unicode(obj), auth=False):
        self.settings[id] = (queryset, fields, limit, key, label, auth)

autocomplete = AutoComplete()
