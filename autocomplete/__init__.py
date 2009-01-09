from django.utils.encoding import smart_unicode

def ac(queryset, fields, limit=None, key='pk', label=lambda obj: smart_unicode(obj), auth=False):
    return (queryset, fields, limit, key, label, auth)
autocomplete = ac
