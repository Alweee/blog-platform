import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post
from users.forms import CreationForm

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='cats',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='dogs',
            description='Тестовое описание',
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            text='Текст комментария',
            author=cls.user,
            post=cls.post
        )
        cls.form = CreationForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        small_gif = self.small_gif
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'test-user'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                image='posts/small.gif'
            ).exists()
        )

    def test_url_pages_show_correct_context(self):
        """Шаблоны страниц сформированы с правильным контекстом"""
        url_names_response = {
            '/': '( ͡° ͜ʖ ͡°)',
            '/group/cats/': '( ͡° ͜ʖ ͡°)',
            '/profile/test-user/': '( ͡° ͜ʖ ͡°)',
        }
        for address, smile in url_names_response.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                first_object = response.context['page_obj'][0]
                post_image_0 = first_object.image
                response = self.authorized_client.get(address)
                self.assertEqual(post_image_0, PostCreateFormTests.post.image)

    def test_posts_detail_page_show_correct_context(self):
        """Шаблон posts:post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        post = response.context['post']
        self.assertEqual(post.image, PostCreateFormTests.post.image)

    def test_valid_form_add_new_post(self):
        """При отправке валидной формы со страницы создания поста
        создаётся новая запись в базе данных"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': PostCreateFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.get(text='Текст из формы')
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'test-user'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(last_post.text, 'Текст из формы')
        self.assertEqual(last_post.group, self.group)

    def test_valid_form_change_post(self):
        """При отправке валидной формы с posts:post_edit
        просисходит изменение поста"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст изменён',
            'group': PostCreateFormTests.group_2.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}))
        self.assertEqual(post.text, 'Тестовый текст изменён')
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post.group, PostCreateFormTests.group_2)
        self.assertEqual(PostCreateFormTests.user, post.author)

    def test_anonymous_user_redirected_at_post_create_url(self):
        """Анонимный пользователь при попытке зайти на страницу 'posts:post_create
        редиректиться на страницу логина'"""
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_only_authorized_user_can_comment(self):
        """Комментировать посты может только авторизованный пользователь"""
        comment_count = Comment.objects.count()
        key_client = {
            'key_0': self.authorized_client,
            'key_1': self.guest_client,
        }
        form_data = {
            'text': 'Комментарий к посту добавлен',
        }
        for key, value in key_client.items():
            with self.subTest(value=value):
                response = value.post(
                    reverse('posts:add_comment', kwargs={'post_id': '1'}),
                    data=form_data,
                    follow=True
                )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_cache_in_home_page(self):
        """Тестирование кеша главной страницы"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.cache = response.content
        cache_post = Post.objects.create(
            text='Текст кешированного поста',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )
        cache_post.delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_2.content, self.cache)
        cache.clear()
        self.assertNotEqual(cache, response_2.content)
