from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.util import flatatt
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from autocomplete.views import autocomplete as default_view



try:
    STATIC_URL = settings.AUTOCOMPLETE_MEDIA_PREFIX
except AttributeError:
    STATIC_URL = settings.STATIC_URL + 'autocomplete/'

class AutocompleteWidget(forms.Widget):

    js_options = {
        'source': None,
        'multiple': False,
        'force_selection': True,
    }

    class Media:
        js = tuple(STATIC_URL + js for js in (
            'js/jquery.min.js',
            'js/jquery-ui.min.js',
            'js/jquery_autocomplete.js',
        ))
        css = {'all':
            (STATIC_URL + 'css/jquery-ui.css',)
        }

    def __init__(self, ac_id, view=default_view, attrs=None, using=None, **js_options):
        self.settings = view.get_settings(ac_id)
        self.db = using
        self.js_options = self.js_options.copy()
        self.js_options.update(self.settings.js_options)
        self.js_options.update(js_options)
        super(AutocompleteWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, hattrs=None, initial_objects=u''):
        if value is None:
            value = ''

        classes = {}
        lookup = ''
        if self.settings.field and self.settings.field.rel:
            if self.js_options['multiple']:
                classes['class'] = 'vManyToManyRawIdAdminField'
            hidden_id = attrs.pop('id', 'id_%s' % name)
            attrs['id'] = 'id_ac_%s' % name

            if self.settings.lookup:
                related_url = '%s%s/%s/' % (reverse('admin:index'),
                                            self.settings.field.rel.to._meta.app_label,
                                            self.settings.field.rel.to._meta.object_name.lower())
                params = self.url_parameters()
                if params:
                    url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in params.items()])
                else:
                    url = ''
                lookup = (u'<a href="%s%s" class="related-lookup" id="lookup_id_%s" '
                          u'onclick="return showRelatedObjectLookupPopup(this);"> '
                          u'<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="%s" />'
                          u'</a>' % (related_url, url, name, settings.ADMIN_MEDIA_PREFIX, _('Lookup')))

        else:
            hidden_id = 'id_hidden_%s' % name
        hidden_attrs = self.build_attrs(classes, type='hidden', name=name, value=value, id=hidden_id)
        normal_attrs = self.build_attrs(attrs, type='text')
        if value:
            if self.settings.reverse_label:
                normal_attrs['value'] = self.label_for_value(value)
            else:
                normal_attrs['value'] = value
        if not self.js_options.get('source'):
            self.js_options['source'] = self.settings.get_absolute_url()
        options = simplejson.dumps(self.js_options)
        return mark_safe(u''.join((
            u'<input%s />\n' % flatatt(hidden_attrs),
            u'<input%s />\n' % flatatt(normal_attrs),
            lookup,
            initial_objects,
            u'<script type="text/javascript">',
            u'django.autocomplete("#%s", %s);' % (attrs['id'], options),
            u'</script>\n',
        )))

    def base_url_parameters(self):
        params = {}
        if self.settings.field.rel.limit_choices_to and hasattr(self.settings.field.rel.limit_choices_to, 'items'):
            items = []
            for k, v in self.settings.field.rel.limit_choices_to.items():
                if isinstance(v, list):
                    v = ','.join([str(x) for x in v])
                else:
                    v = str(v)
                items.append((k, v))
            params.update(dict(items))
        return params

    def url_parameters(self):
        from django.contrib.admin.views.main import TO_FIELD_VAR
        params = self.base_url_parameters()
        params.update({TO_FIELD_VAR: self.settings.field.rel.get_related_field().name})
        return params

    def label_for_value(self, value):
        # XXX MultipleObjectsReturned could be raised if the field is not unique.
        settings = self.settings
        try:
            obj = settings.queryset.get(**{settings.key: value})
            return settings.value(obj)
        except settings.model.DoesNotExist:
            return value


class MultipleAutocompleteWidget(AutocompleteWidget):

    def __init__(self, ac_id, view=default_view, attrs=None, using=None, **js_options):
        js_options['multiple'] = True
        super(MultipleAutocompleteWidget, self).__init__(ac_id, view, attrs,
            using, **js_options)

    def render(self, name, value, attrs=None, hattrs=None):
        if value:
            initial_objects = self.initial_objects(value)
            value = ','.join([str(v) for v in value])
        else:
            value = None
            initial_objects = u''
        return super(MultipleAutocompleteWidget, self).render(
            name, value, attrs, hattrs, initial_objects)

    def url_parameters(self):
        return self.base_url_parameters()

    def label_for_value(self, value):
        return ''

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            return value.split(',')
        return value

    def initial_objects(self, value):
        settings = self.settings
        output = [u'<table class="ui-autocomplete-values">']
        for obj in settings.queryset.filter(**{'%s__in' % settings.key: value}):
            output.append(u'<tr><td>%s</td></tr>' % settings.label(obj).replace(u'\t', u'</td><td>'))
        output.append(u'</table>\n')
        return mark_safe(u'\n'.join(output))

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        initial_set = set([force_unicode(value) for value in initial])
        data_set = set([force_unicode(value) for value in data])
        return data_set != initial_set
