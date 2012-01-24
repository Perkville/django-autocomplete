from os.path import splitext

import django
from django.db import models
from django.contrib import admin
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _

from autocomplete import widgets
from autocomplete.views import autocomplete as default_view
from autocomplete.utils import autocomplete_formfield


class AdminMedia:
    extend = False
    js = (widgets.STATIC_URL + 'js/jquery_autocomplete.js',)
    css = {'all':
        (widgets.STATIC_URL + 'css/jquery-ui.css',)
    }

class AdminAutocompleteWidget(widgets.AutocompleteWidget):
    Media = AdminMedia

class AdminMultipleAutocompleteWidget(widgets.MultipleAutocompleteWidget):
    Media = AdminMedia


class AutocompleteAdmin(object):
    autocomplete_autoconfigure = True
    autocomplete_view = default_view
    autocomplete_fields = {}

    def autocomplete_formfield(self, ac_id, formfield=None, options=None, **kwargs):
        if options is not None:
            kwargs['options'] = options
        formfield = autocomplete_formfield(ac_id, formfield, self.autocomplete_view,
                AdminAutocompleteWidget, AdminMultipleAutocompleteWidget, **kwargs)
        if (self.autocomplete_view.settings[ac_id].add_button and
            isinstance(ac_id, (models.ForeignKey, models.ManyToManyField)) and
            formfield and ac_id.name not in self.raw_id_fields):
            request = kwargs.get("request", None)
            related_modeladmin = self.admin_site._registry.get(
                ac_id.rel.to)
            can_add_related = bool(related_modeladmin and
                related_modeladmin.has_add_permission(request))
            if django.VERSION[1] > 2:   # for django 1.3+
                formfield.widget = admin.widgets.RelatedFieldWidgetWrapper(
                    formfield.widget, ac_id.rel, self.admin_site,
                    can_add_related=can_add_related)
            elif can_add_related:
                formfield.widget = admin.widgets.RelatedFieldWidgetWrapper(
                    formfield.widget, ac_id.rel, self.admin_site)
        if not isinstance(ac_id, basestring):
            self._set_help_text(ac_id, formfield)
        return formfield

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.autocomplete_fields:
            ac_id = self.autocomplete_fields[db_field.name]
            options = None
            if not ac_id:
                options = {}
            elif isinstance(ac_id, dict):
                options = ac_id
            elif isinstance(ac_id, (tuple, list)):
                options = {'search_fields': ac_id}
            elif isinstance(ac_id, basestring) and ac_id in self.model._meta.get_all_field_names():
                options = {'search_fields': (ac_id,)}
            if options is not None:
                return self.autocomplete_formfield(db_field, options=options, **kwargs)
            return self.autocomplete_formfield(ac_id, db_field.formfield, **kwargs)
        elif self.autocomplete_autoconfigure:
            if db_field in self.autocomplete_view.settings:
                return self.autocomplete_formfield(db_field, **kwargs)
        return super(AutocompleteAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def _set_help_text(self, db_field, formfield):
        """
        Set the help text from the model Field. If it's a ManyToManyField use
        an ugly hack to remove or change the default help text impose
        by this Field type. See Django bug #9321.
        
        class MyModel(models.Model):
            no_help_text = models.ManyToManyField()
                -> help_text = ''
                
            defautl_help_text = models.ManyToManyField(help_text=u'.')
                -> help_text = u'Field with autocompletion. Start typing text to get suggestions.'
                
            my_help_text = models.ManyToManyField(help_text=u'My help text.')
                -> help_text = u'My help text.'
                
        In the last case, help_text should be finished by a dot.
        If not, strange things can happen.
        """
        if isinstance(db_field, models.ManyToManyField):
            help_text = smart_unicode(formfield.help_text[:-1]) # remove the last dot.
            if help_text.startswith('.'):
                help_text = _(u'Field with autocompletion. Start typing text to get suggestions.')
            elif '.' in help_text:
                help_text = u'%s.' % splitext(help_text)[0]
            else:
                help_text = u''
        else:
            help_text = smart_unicode(db_field.help_text)
        formfield.help_text = help_text

    def _media(self):
        # little hack to include autocomplete's js before jquery.init.js
        media = super(AutocompleteAdmin, self).media
        media._js.insert(3, widgets.STATIC_URL + 'js/jquery-ui.min.js')
        return media
    media = property(_media)

    def _autocomplete_view(request, field):
        info = self.model._meta.app_label, self.model._meta.module_name, field

        if field in self.autocomplete_fields:
            ac_id = self.autocomplete_fields[field]
        else:
            ac_id = '/'.join(info)
        return self.autocomplete_view(request, ac_id)

    def get_urls(self):
        # This ensures that `admin_site.admin_view` is applied to the
        # autocomplete_view.
        from django.conf.urls.defaults import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = super(AutocompleteAdmin, self).get_urls()
        urlpatterns += patterns('',
            url(r'^autocomplete/(?P<field>[\w]+)/$',
                self.admin_site.admin_view(self._autocomplete_view),
                name='%s_%s_autocomplete' % info)
        )
        return urlpatterns

    def urls(self):
        return self.get_urls()
    urls = property(urls)

    @classmethod
    def _validate(self):
        pass
