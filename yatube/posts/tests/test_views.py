import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def check_context_pages(obj, context, image=False):
    """Функция проверяет контест поста на наличие полей модели."""
    contex_author = context.author
    contex_group = context.group
    contex_text = context.text
    obj.assertEqual(contex_author, obj.post.author)
    obj.assertEqual(contex_group, obj.post.group)
    obj.assertEqual(contex_text, obj.post.text)
    if image:
        context_image = context.image
        obj.assertTrue(context_image)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='auth')
        cls.second_user = User.objects.create_user(username='noName')
        cls.first_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.second_group = Group.objects.create(
            title='Тестовая группа #2',
            slug='test-slug1',
            description='Тестовое описание',
        )
        cls.small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.second_user,
            group=cls.first_group,
            text='Тестовый пост с большим количеством символов.',
            image=cls.uploaded
        )
        cls.templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_pages',
                kwargs={
                    'slug': cls.first_group.slug
                }
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={
                    'username': cls.second_user.username
                }
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': cls.post.id
                }
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': cls.post.id
                }
            ): 'posts/create_post.html'
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.second_user)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_templates_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                try:
                    context_obj = response.context.get('page_obj')[0]
                except TypeError:
                    if template != 'posts/post_detail.html':
                        for value, expected in form_fields.items():
                            with self.subTest(value=value):
                                form_field = response.context.get(
                                    'form').fields.get(value)
                                self.assertIsInstance(form_field, expected)
                        continue
                    context_obj = response.context.get('post')
                check_context_pages(self, context_obj, image=True)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.COUNT_POSTS_WITH_GROUP = settings.COUNT_OF_VISIBLE_POSTS + 1
        cls.COUNT_POSTS_ALL = cls.COUNT_POSTS_WITH_GROUP + 2
        Post.objects.bulk_create(
            [Post(
                author=cls.user,
                group=cls.group,
                text=f'Тестовый пост #{post_number}.'
            ) if post_number < cls.COUNT_POSTS_WITH_GROUP else Post(
                author=cls.user,
                text=f'Тестовый пост #{post_number}.'
            ) for post_number in range(cls.COUNT_POSTS_ALL)]
        )
        cls.first_views_names = (
            reverse('posts:index'),
            reverse(
                'posts:group_pages',
                kwargs={'slug': 'test-slug'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            )
        )
        cls.second_views_names = (
            elem + '?page=2' for elem in cls.first_views_names
        )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_first_page_contains_settings_records(self):
        """Проверяем, что первая страница содержит количество постов,
        указанное в настройках для пагинатора.
        """
        for reverse_name in self.first_views_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.COUNT_OF_VISIBLE_POSTS)

    def test_second_page_contains_remains(self):
        """Проверяем, что вторая страница содержит количество постов,
        оставшееся после отображения на первой странице.
        """
        no_group = self.COUNT_POSTS_WITH_GROUP
        all_posts = settings.COUNT_OF_VISIBLE_POSTS
        for reverse_name in self.second_views_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                if 'group' in reverse_name:
                    self.assertEqual(
                        len(response.context['page_obj']),
                        no_group - all_posts
                    )
                    continue
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.COUNT_POSTS_ALL - settings.COUNT_OF_VISIBLE_POSTS
                )


class CheckCreationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.first_group = Group.objects.create(
            title='Тестовая группа #1',
            slug='test-slug-1',
            description='Тестовое описание #1',
        )
        cls.second_group = Group.objects.create(
            title='Тестовая группа #2',
            slug='test-slug-2',
            description='Тестовое описание #2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.first_group,
            text='Тестовый пост с большим количеством символов.',
        )
        cls.views_names = (
            reverse('posts:index'),
            reverse(
                'posts:group_pages',
                kwargs={'slug': cls.first_group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            )
        )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_creation_record_will_pages(self):
        """Проверяем, что при указании группы пост появляется
        на главной странице, странице выбранной группы, в профиле.
        """
        for reverse_name in self.views_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                contex_obj = response.context.get('page_obj')[0]
                check_context_pages(self, contex_obj)

    def test_creation_record_with_group_not_will_another_group_page(self):
        """Проверяем, что при указании группы пост не появится
        на странице другой группы.
        """
        response_first = self.guest_client.get(
            reverse(
                'posts:group_pages',
                kwargs={'slug': self.first_group.slug})
        )
        response_second = self.guest_client.get(
            reverse(
                'posts:group_pages',
                kwargs={'slug': self.second_group.slug})
        )
        context_first = response_first.context.get('page_obj')
        context_second = response_second.context.get('page_obj')
        self.assertNotEqual(
            len(context_first),
            len(context_second),
            'Пост появился в двух группах.'
        )


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с большим количеством символов.',
        )
        cls.views = reverse('posts:index')

    def setUp(self):
        self.guest_client = Client()
        # cache.clear()
    
    def test_cache_index_page(self):
        """Проверяем работу кеша через удаление записи."""
        responce = self.guest_client.get(self.views)
        print(responce.content)