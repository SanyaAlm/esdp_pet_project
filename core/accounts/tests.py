from django.test import TestCase
from django.urls import reverse
from .models import User


class LoginTestCase(TestCase):
    def setUp(self):
        self.username = 'username@gmail.com'
        self.password = '123123'
        self.user = User.objects.create_user(email=self.username, password=self.password, phone='77058788787')

        self.login_url = reverse('login')

    def test_user_login(self):
        data = {'username': self.username, 'password': self.password}

        response = self.client.post(self.login_url, data)

        self.assertRedirects(response, reverse('sms-verification'))

    def test_user_login_fail(self):
        data = {'username': self.username, 'password': 'wrongpass'}

        response = self.client.post(self.login_url, data)

        self.assertContains(response, 'Пожалуйста, введите правильные Email и пароль. '
                                      'Оба поля могут быть чувствительны к регистру.')


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.registration_url = reverse('register')

    def test_registration_success(self):

        data = {'first_name': 'John', 'last_name': 'Doe',
                'phone': '77054779047', 'email': 'johndoe@gmail.com',
                'password1': '123', 'password2': '123'}

        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('sms-verification'))

    def test_registration_fail(self):

        data = {'first_name': 'John', 'last_name': 'Doe',
                'phone': '123', 'email': 'johndoe@gmail.com',
                'password1': '123', 'password2': '123'}
        response = self.client.post(self.registration_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Номер телефона должен быть в формате: +7XXXXXXXXXX')

    def test_registration_fail_password(self):

        data = {'first_name': 'John', 'last_name': 'Doe',
                'phone': '123', 'email': 'johndoe@gmail.com',
                'password1': '123', 'password2': '2222'}
        response = self.client.post(self.registration_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Введенные пароли не совпадают.')
