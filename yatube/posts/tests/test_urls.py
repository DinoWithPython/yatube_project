from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='auth')
        cls.second_user = User.objects.create_user(username='noName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post_first = Post.objects.create(
            author=cls.first_user,
            text='Тестовый пост с большим количеством символов.'
        )
        cls.post_second = Post.objects.create(
            author=cls.second_user,
            text='Тестовый пост авторизованного second_user'
        )
        cls.templates_url_auth = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.second_user.username}/': 'posts/profile.html',
            f'/posts/{cls.post_first.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            # Создал first_user
            f'/posts/{cls.post_first.id}/edit/': f'/posts/'
                                                 f'{cls.post_first.id}/',
            # Создал second_user
            f'/posts/{cls.post_second.id}/edit/': 'posts/create_post.html'
        }
        cls.templates_url_not_auth = {
            adress: template for adress, template in list(
                cls.templates_url_auth.items())[:5]
            + [('/create/', '/auth/login/?next=/create/')]
            + [(f'/posts/{cls.post_first.id}/edit/',
                f'/auth/login/?next=/posts/{cls.post_first.id}/edit/')]
            + [(f'/posts/{cls.post_first.id}/comment/',
                f'/auth/login/?next=/posts/{cls.post_first.id}/comment/')]
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.second_user)

    def test_urls_with_subtests(self):
        """Проверки доступности адресов, корректности шаблонов, редиректов."""
        for address, template in self.templates_url_auth.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                if address == f'/posts/{self.post_first.id}/edit/':
                    self.assertEqual(response.status_code,
                                     HTTPStatus.FOUND.value)
                    self.assertRedirects(response, template)
                    continue
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK.value)
                self.assertTemplateUsed(response,
                                        template)
        for address, template in self.templates_url_not_auth.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if address in ('/create/',
                               f'/posts/{self.post_first.id}/edit/',
                               f'/posts/{self.post_first.id}/comment/'):
                    self.assertEqual(response.status_code,
                                     HTTPStatus.FOUND.value)
                    self.assertRedirects(response, template)
                    continue
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK.value)
                self.assertTemplateUsed(response,
                                        template)

    def test_unexpecting_page(self):
        """Не существующая страница вернет ошибку 404."""
        response = self.guest_client.get('/test_not_using_page/')
        self.assertEqual(response.status_code,
                         HTTPStatus.NOT_FOUND.value,
                         'К несуществуещей странице должен вернуться 404')
