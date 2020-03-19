from django.test import Client, TestCase
from users.forms import CustomUserCreationForm
from django.urls import reverse

from .models import CustomUser
# Create your tests here.

class UserSignUp(TestCase):

    def setUp(self):
        self.client = Client()

    def test_form_passed_in_context(self):
        path = reverse('users:signup')
        print("path = ", path)
        response = self.client.get(path)
        self.assertIn('form', response.context)

    def test_uses_signin_template(self):
        path = reverse('users:signup')
        response = self.client.get(path)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_CustomUserCreationForm_saves_form_data(self):
        path = reverse('users:signup')
        response = self.client.post(path, data={'username': 'test_username',
                                                'email':'test@test.com',
                                                'password1':'Belgrade2010',
                                                'password2':'Belgrade2010'
        })
        username=CustomUser.objects.get(username='test_username').username
        self.assertEqual(username, 'test_username')


class UserDashboardView(TestCase):

    def setUp(self):
        self.client = Client()
        user = CustomUser.objects.create_user('test_UserProfile',
                                              email='a@a.net',
                                              password='abc123')
        user.save
        self.client.login(username='test_UserProfile', password='abc123')

    def test_template_used(self):
        path = reverse('users:dashboard')
        response = self.client.get(path)
        self.assertTemplateUsed(response, 'registration/dashboard.html')

    def test_username_passed_in_context(self):
        path = reverse('users:dashboard')
        response = self.client.get(path)
        self.assertIn('username', response.context)

    def test_link_to_quiz_on_page(self):
        response = self.client.get('/account/')
        self.assertIn(b'<a href="/quiz/"', response.content)

class UserResultsView(TestCase):

    def setUp(self):
        self.client = Client()
        user = CustomUser.objects.create_user('test_UserProfile',
                                              email='a@a.net',
                                              password='abc123')
        user.save
        self.client.login(username='test_UserProfile', password='abc123')

    def test_results_page_has_test_results_shown(self):
        response = self.client.get('/account/results/')
