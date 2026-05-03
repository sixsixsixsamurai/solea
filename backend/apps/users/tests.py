from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import RegisterForm

User = get_user_model()


class RegisterFormTest(TestCase):
    def test_valid_form(self):
        form = RegisterForm(data={
            'username': 'newuser',
            'email': 'user@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        self.assertTrue(form.is_valid())

    def test_passwords_do_not_match(self):
        form = RegisterForm(data={
            'username': 'newuser',
            'password': 'securepass123',
            'password_confirm': 'differentpass',
        })
        self.assertFalse(form.is_valid())

    def test_password_too_short(self):
        form = RegisterForm(data={
            'username': 'newuser',
            'password': 'short',
            'password_confirm': 'short',
        })
        self.assertFalse(form.is_valid())

    def test_duplicate_username(self):
        User.objects.create_user(username='existinguser', password='pass12345')
        form = RegisterForm(data={
            'username': 'existinguser',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        self.assertFalse(form.is_valid())

    def test_email_not_required(self):
        form = RegisterForm(data={
            'username': 'newuser',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        self.assertTrue(form.is_valid())


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_redirects_after_success(self):
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_register_redirects_authenticated_user(self):
        User.objects.create_user(username='existing', password='pass12345')
        self.client.login(username='existing', password='pass12345')
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 302)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page_loads(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_valid_login_redirects(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_login_stays_on_page(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_invalid_login_shows_error_message(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        messages = list(response.context['messages'])
        self.assertTrue(any('Invalid' in str(m) for m in messages))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])

    def test_profile_accessible_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
