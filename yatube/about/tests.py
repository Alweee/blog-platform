from http import HTTPStatus

from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url_correct(self):
        """Проверка доступности любому польз-лю адреса url /about/author/."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_url_correct(self):
        """Проверка доступности любому пользователю адреса url /about/tech/."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
