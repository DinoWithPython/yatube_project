import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTest(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.first_user,
            group=cls.group,
            text='Тестовый пост с большим количеством символов.'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.second_user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_add_database(self):
        """Проверка записи поста в БД."""
        posts_count = Post.objects.count()
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'author': self.second_user,
            'group': self.group.id,
            'text': 'Тестовый пост',
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        latest_post = Post.objects.latest('id')
        self.assertEqual(latest_post.author.username,
                         self.second_user.username)
        self.assertEqual(latest_post.group.id, self.group.id)
        self.assertEqual(latest_post.text, form_data['text'])
        self.assertTrue(latest_post.image)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_form_change_record_in_database(self):
        """Проверка изменения записи в БД, при изменении её пользователем."""
        new_post = Post.objects.create(
            author=self.second_user,
            text='Тестовый.'
        )
        form_data = {
            'author': self.second_user,
            'group': self.group.id,
            'text': 'Тестовый пост изменён!'
        }
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': new_post.id}
            ),
            data=form_data
        )
        post_from_db = Post.objects.filter(id=new_post.id)[0]
        self.assertEqual(post_from_db.id, new_post.id)
        self.assertEqual(
            post_from_db.author.username,
            new_post.author.username)
        self.assertEqual(post_from_db.group, self.group)
        self.assertEqual(post_from_db.text, form_data['text'])

    def test_non_auth_can_not_send_post(self):
        """Проверяем, что не авторизованный не может создать пост
        отправкой формы.
        """
        form_data = {
            'author': self.second_user,
            'group': self.group.id,
            'text': 'Не авторизованные рулят!'
        }
        non_auth_post = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertNotIsInstance(non_auth_post, Post)

    def test_add_comment(self):
        """Проверяем, что комментарий можно оставить и он будет в контексте."""
        count_comments = Comment.objects.count()
        form_data = {
            'text': 'Супер коммент!'
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.id,
                }
            ),
            data=form_data
        )
        comment_form = Comment.objects.latest('id')
        self.assertEqual(form_data['text'], comment_form.text)
        self.assertEqual(Comment.objects.count(), count_comments + 1)
