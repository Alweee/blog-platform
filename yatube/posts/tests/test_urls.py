from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_2 = User.objects.create_user(username='another_user')
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='cats',
            description='Тестовое описание',
        )
        Post.objects.create(
            text='Тестовый текст',
            pub_date='Тестовый pub_date',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(TaskURLTests.user)
        self.authorized_client_2.force_login(TaskURLTests.user_2)

    def test_urls_uses_correct_template(self):
        """URL-адреса использует соответствующие шаблоны."""
        url_names_templates = {
            '/': 'posts/index.html',
            '/group/cats/': 'posts/group_list.html',
            '/profile/test-user/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/page/404/': 'core/404.html',
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_code_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_accessed_for_authorized_user(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_accessed_for_author(self):
        """Страница posts:post_edit доступна автору поста."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_if_not_author(self):
        """Страница posts:post_edit редиректит, если это не автор."""
        response = self.authorized_client_2.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, ('/posts/1/'))
