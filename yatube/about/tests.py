from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_page_availability_for_all(self):
        """Проверка доступности страниц автора и технологий"""
        tuple_pages = (
            '/about/author/',
            '/about/tech/'
        )
        for URL in tuple_pages:
            response = self.guest_client.get(URL)
            self.assertEqual(response.status_code,
                             HTTPStatus.OK.value,
                             f'{URL} работает не правильно')

    def test_urls_uses_correct_template(self):
        """Проверка корректности используемых шаблонов."""
        templates_url_not_auth = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in templates_url_not_auth.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response,
                                        template)
