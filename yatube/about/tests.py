from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_url = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

    def setUp(self):
        self.guest_client = Client()

    def test_page_availability_for_all(self):
        """Проверка доступности страниц автора и технологий"""
        for URL in self.templates_url.keys():
            response = self.guest_client.get(URL)
            self.assertEqual(response.status_code,
                             HTTPStatus.OK.value,
                             f'{URL} работает не правильно')

    def test_urls_uses_correct_template(self):
        """Проверка корректности используемых шаблонов."""
        for address, template in self.templates_url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response,
                                        template)
