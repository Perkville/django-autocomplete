from django.forms import widgets
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.forms.util import flatatt


# FIXME not ready for admin edit page, need ac_id_%(name)s prefill (2 line of js).

AC_TEMPLATE = u'''
<div>
  <input type="hidden" name="%(name)s" id="id_hidden_%(name)s" />
  <input type="text" id="id_%(name)s" %(attrs)s />
  <script type="text/javascript">autocomplete("%(name)s", "%(url)s", %(force_selection)s);</script>
</div>
'''

class AutoCompleteWidget(widgets.Widget):

    AC_TEMPLATE = AC_TEMPLATE

    class Media:
        css = {'all':
            ("http://yui.yahooapis.com/2.6.0/build/autocomplete/assets/skins/sam/autocomplete.css",)
        }
        js = ('http://yui.yahooapis.com/combo'
              '?2.6.0/build/yahoo-dom-event/yahoo-dom-event.js'
              # decomment to enable animation.
              #'&2.6.0/build/animation/animation-min.js'
              '&2.6.0/build/connection/connection-min.js'
              '&2.6.0/build/datasource/datasource-min.js'
              '&2.6.0/build/autocomplete/autocomplete-min.js',
              'js/autocomplete.js')

    def __init__(self, ac_name, force_selection=True, view_name='autocomplete', attrs=None):
        super(AutoCompleteWidget, self).__init__(attrs)
        self.ac_name = ac_name
        self.view_name = view_name
        self.force_selection = force_selection
    
    def render(self, name, value, attrs=None, choices=()):
        #input = super(AutoComplete, self).render(name, value, attrs)
        url = reverse(self.view_name, args=[self.ac_name])
        force_selection = ['false', 'true'][self.force_selection]
        if value:
            attrs['value'] = force_unicode(value)
        del value
        attrs = flatatt(self.build_attrs(attrs))
        return mark_safe(self.AC_TEMPLATE % locals())

