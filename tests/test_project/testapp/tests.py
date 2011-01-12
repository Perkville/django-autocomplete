# -*- coding: utf-8 -*-
from unittest import TestCase
from django.test import TestCase as DjangoTestCase
from django import forms

from autocomplete import widgets, utils

from test_project.testapp import widgets as custom_widgets
from test_project.testapp.views import autocomplete
from test_project.testapp.models import Dummy

# TODO:
# test decorated view Settings.view
# test case sensitive/insensitive
# test unicode
# TestCase for autocomplete.widgets
# TestCase for AutocompleteView API
# TestCase for autocomplete.admin
# TestCase for autocomplete.utils

class AutocompleteViewTests(DjangoTestCase):

    ac_url = '/testapp/autocomplete/testapp'
    def ac_request(self, path, term='random_query'):
        return self.client.get('%s/%s/' % (self.ac_url, path), {'term': term})

    def test_mimetype(self):
        response = self.ac_request('simple')
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_login_required(self):
        self.client.login(username='testuser', password='testpass')
        response = self.ac_request('loginreq')
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_forbidden(self):
        response = self.ac_request('loginreq')
        self.assertEqual(response.status_code, 403)

    def test_matching_term(self):
        response = self.ac_request('simple', 'g')
        self.assertContains(response, 'gayle_burger')
        self.assertContains(response, 'gary_vecchiarelli')
        self.assertContains(response, r'gl\u00ea\u00f1_z\u00ebpk\u00e3')
    
    def test_non_matching_term(self):
        response = self.ac_request('simple', '*nonexistent-username*')
        self.assertEqual(response.content, '[]')

    def test_custom_has_permission(self):
        self.client.login(username='super', password='secret')
        response = self.ac_request('hasperm')
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_custom_forbidden(self):
        response = self.ac_request('hasperm')
        self.assertTemplateUsed(response, 'autocomplete/forbidden.html')
        self.assertContains(response, 'testapp.hasperm', status_code=403)

    def test_not_found(self):
        response = self.ac_request('*no-matching-settings*')
        self.assertEqual(response.status_code, 404)

    def test_custom_key(self):
        response = self.ac_request('customrender', 'g')
        self.assertContains(response, '"id": "Gayle"')
        self.assertContains(response, r'"id": "Gl\u00ea\u00f1"')

    def test_custom_value(self):
        response = self.ac_request('customrender', 'g')
        self.assertContains(response, '"value": "GAYLE_BURGER"')
        self.assertContains(response, r'"value": "GL\u00ca\u00d1_Z\u00cbPK\u00c3"')

    def test_custom_label(self):
        response = self.ac_request('customrender', 'g')
        self.assertContains(response, '"label": "<em>gayle@burger.com</em>"')
        self.assertContains(response, r'"label": "<em>gl\u00ea\u00f1@z\u00ebpk\u00e3.com</em>"')

    def test_limit_choices_to(self):
        response = self.ac_request('dummy/user2', 'g')
        self.assertContains(response, 'gayle_burger')
        self.assertContains(response, 'gary_vecchiarelli')
        self.assertContains(response, r'gl\u00ea\u00f1_z\u00ebpk\u00e3')
    
    def test_limit_choices_to_empty(self):
        response = self.ac_request('dummy/user2', 'f')
        self.assertEqual(response.content, '[]')

    def test_limit(self):
        response = self.ac_request('limit', 'g')
        self.assertContains(response, 'gary')
        self.assertNotContains(response, 'gayle')
        self.assertNotContains(response, r'gl\u00ea\u00f1')


class AutocompleteFormfieldTests(DjangoTestCase):

    def setUp(self):
        import test_project.testapp.autocomplete_settings
    
    def assertIsInstance(self, obj, cls):
        """Same as self.assertTrue(isinstance(obj, cls)), with a nicer
           default message."""
        if not isinstance(obj, cls):
            standardMsg = '%r is not an instance of %r' % (obj, cls)
            self.fail(standardMsg)

    def test_inexistent_settings(self):
        self.assertRaises(KeyError, utils.autocomplete_formfield,
            'testapp.simple')

    def test_default_values(self):
        formfield = utils.autocomplete_formfield(Dummy.user2,
            view=autocomplete)
        self.assertIsInstance(formfield, forms.ModelChoiceField)
        self.assertIsInstance(formfield.widget, widgets.AutocompleteWidget)
        
        formfield = utils.autocomplete_formfield(Dummy.friends,
            view=autocomplete)
        self.assertIsInstance(formfield, forms.ModelMultipleChoiceField)
        self.assertIsInstance(formfield.widget, widgets.MultipleAutocompleteWidget)

        formfield = utils.autocomplete_formfield('testapp.customrender',
            view=autocomplete)
        self.assertIsInstance(formfield, forms.CharField)
        self.assertIsInstance(formfield.widget, widgets.AutocompleteWidget)

        formfield = utils.autocomplete_formfield('testapp.email',
            view=autocomplete)
        self.assertIsInstance(formfield, forms.CharField)
        self.assertIsInstance(formfield.widget, widgets.AutocompleteWidget)

    def test_custom_widgets(self):
        formfield = utils.autocomplete_formfield('testapp.simple',
            widget_class=custom_widgets.CustomAutocompleteWidget,
            view=autocomplete)
        self.assertIsInstance(formfield.widget,
            custom_widgets.CustomAutocompleteWidget)

        formfield = utils.autocomplete_formfield(Dummy.friends,
            multiple_widget_class=custom_widgets.CustomMultipleAutocompleteWidget,
            view=autocomplete)
        self.assertIsInstance(formfield.widget,
            custom_widgets.CustomMultipleAutocompleteWidget)

    def test_custom_formfield(self):
        formfield = utils.autocomplete_formfield('testapp.email', forms.EmailField,
            view=autocomplete)
        self.assertIsInstance(formfield, forms.EmailField)
