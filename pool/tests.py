
from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
import requests

from pool import models
from pool import views

class UserTestCase(TestCase):
    """
    A unit test case for the User and Organization User models.
    """
    def setUp(self):
        models.Organization.objects.create(organization_name="The New York Times", organization_type="p")
        self.factory = RequestFactory()

    def test_create_user_page(self):
        request = self.factory.get('/pool/user/create/')
        response = views.create_user(request)

        # The create user page returns a valid response to GET.
        self.assertEqual(response.status_code, 200)

    def test_create_user_error(self):
        user_data = {}
        request = self.factory.post('/pool/user/create/', user_data)
        response = views.create_user(request)

        # Even with a blank request, the page returns a 200.
        self.assertEqual(response.status_code, 200)

        # The page explains we're missing parameters.
        self.assertIn('you\'re missing a parameter', str(response))

    def test_create_user(self):
        user_data = {}
        user_data['first_name'] = 'Jeremy'
        user_data['last_name'] = 'Bowers'
        user_data['email_address'] = 'jeremyjbowers@gmail.com'
        user_data['username'] = 'jbowers'
        user_data['phone_number'] = '555-555-5555'
        user_data['preferred_contact'] = 'e'
        user_data['organization_id'] = '2'
        user_data['password'] = 'passw0rd!'
        user_data['shared_secret'] = settings.SHARED_SECRET

        # So as not to send an email.
        user_data['test'] = True

        request = self.factory.post('/pool/user/create/', user_data)
        response = views.create_user(request)

        # Should have a 200.
        self.assertEqual(response.status_code, 200)

        # Tests for special text in the response body.
        # This would be the body of a success email.
        self.assertIn('If this was you, please click this link to verify your account.', str(response))

        # Creates exactly one OrganizationUser.
        self.assertEqual(1, models.OrganizationUser.objects.all().count())

        # The OrganizationUser's special code is in the email body.
        self.assertIn(models.OrganizationUser.objects.all()[0].temporary_code, str(response))

    def test_login_user(self):
        pass

    def test_logout_user(self):
        pass

    def test_verify_user(self):
        pass

    def test_create_organization_user(self):
        pass

    def test_preferred_contact_method(self):
        pass