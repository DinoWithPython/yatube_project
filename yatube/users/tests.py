from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='noName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_availability_for_all(self):
        """Проверка доступности страниц регистрации и авторизации для всех."""
        tuple_pages = (
            '/auth/signup/',
            '/auth/login/'
        )
        for URL in tuple_pages:
            response = self.guest_client.get(URL)
            self.assertEqual(response.status_code,
                             HTTPStatus.OK.value,
                             f'{URL} работает не правильно')

    def test_page_availability_for_auth(self):
        """Проверка доступности старниц для авторизованных."""
        tuple_pages = (
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
            '/auth/logout/'
        )
        for URL in tuple_pages:
            response = self.authorized_client.get(URL)
            self.assertEqual(response.status_code,
                             HTTPStatus.OK.value,
                             f'{URL} работает не правильно')

    def test_urls_uses_correct_template_non_auth(self):
        """Проверка корректности шаблонов для всех."""
        templates_url_not_auth = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html'
        }
        for address, template in templates_url_not_auth.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response,
                                        template)

    def test_urls_uses_correct_template_auth(self):
        """Проверка корректности шаблонов для авторизованных."""
        templates_url_not_auth = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html'
        }
        for address, template in templates_url_not_auth.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response,
                                        template)
