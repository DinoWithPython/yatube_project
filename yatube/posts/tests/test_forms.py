from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


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

    def test_post_add_database(self):
        """Проверка записи поста в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'author': self.second_user,
            'group': self.group.id,
            'text': 'Тестовый пост'
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
