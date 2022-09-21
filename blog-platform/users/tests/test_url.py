from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_pages(self):
        """Тестирование общедоступных страниц"""
        url_names_code = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
        }
        for key, value in url_names_code.items():
            with self.subTest(key=key):
                response = self.guest_client.get(key)
                self.assertEqual(response.status_code, value)

    def test_redirect_anonymous_pages(self):
        """Страницы /password_change/, /password_change/done/
        перенаправляют анонимного польз-ля на страницу логина."""
        url_names_redirect_page = {
            '/auth/password_change/': '/auth/login/?next=/auth/'
                                      'password_change/',
            '/auth/password_change/done/': '/auth/login/?next=/auth/'
                                           'password_change/done/',
        }
        for key, value in url_names_redirect_page.items():
            with self.subTest(key=key):
                response = self.guest_client.get(key, follow=True)
                self.assertRedirects(
                    response, (value))
