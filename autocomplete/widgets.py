from django import forms
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


# FIXME not ready for admin edit page, need ac_id_%(name)s prefill (2 line of js).

class ModelAutoComplete(forms.Select):

    class Media:
        css = {'all':
            ("http://yui.yahooapis.com/2.6.0/build/autocomplete/assets/skins/sam/autocomplete.css",)
        }
        js = ('http://yui.yahooapis.com/combo'
              '?2.6.0/build/yahoo-dom-event/yahoo-dom-event.js'
              '&2.6.0/build/animation/animation-min.js'
              '&2.6.0/build/connection/connection-min.js'
              '&2.6.0/build/datasource/datasource-min.js'
              '&2.6.0/build/autocomplete/autocomplete-min.js',
              'js/autocomplete.js')

    def __init__(self, ac_name, attrs=None, view_name='autocomplete'):
        super(ModelAutoComplete, self).__init__(attrs, ())
        self.ac_name = ac_name
        self.view_name = view_name
    
    def render(self, name, value, attrs=None, choices=()):
        output = [super(ModelAutoComplete, self).render(name, value, attrs, choices)]
        output.append(u'<input type="text" id="id_ac_%s" style="display:none" />\n' % (name))
        output.append(u'<script type="text/javascript">autocomplete("%s", "%s");</script>\n' %
            (name, reverse(self.view_name, args=[self.ac_name])))
        return mark_safe(u''.join(output))

