from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.another_user = User.objects.create_user(username='another-user')
        cls.user_2 = User.objects.create_user(username='test_2-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='cats',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Тестовая группа',
            slug='dogs',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.another_post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user_2,
            group=cls.group,
        )
        cls.follow = Follow.objects.create(
            user=cls.another_user,
            author=cls.user_2,
        )
        cls.posts = []
        for i in range(12):
            cls.posts.append(Post(
                text='Тестовый пост',
                author=cls.user,
                group=cls.group))
        Post.objects.bulk_create(cls.posts)

        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.authorized_client_2.force_login(PostPagesTests.another_user)

    def test_url_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'cats'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'test-user'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_use_correct_template(self):
        """URL-адрес использует шаблон posts/create_post.html."""
        response = self.authorized_client.\
            get(reverse('posts:post_edit', kwargs={'post_id': '1'}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_home_page_show_correct_context(self):
        """Шаблон posts:index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post_object = response.context['page_obj'][0]
        post_author_0 = first_post_object.author
        post_group_0 = first_post_object.group
        post_text_0 = first_post_object.text
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)
        self.assertEqual(post_text_0, 'Тестовый пост')

    def test_posts_group_list_page_show_correct_context(self):
        """Шаблон posts:group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'cats'}))
        first_post_object = response.context['page_obj'][0]
        post_author_0 = first_post_object.author
        post_group_0 = first_post_object.group
        post_text_0 = first_post_object.text
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)
        self.assertEqual(post_text_0, 'Тестовый пост')

    def test_posts_profile_page_show_correct_context(self):
        """Адрес posts:profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'test-user'}))
        first_post_object = response.context['page_obj'][0]
        post_author_0 = first_post_object.author
        post_group_0 = first_post_object.group
        post_text_0 = first_post_object.text
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)
        self.assertEqual(post_text_0, 'Тестовый пост')

    def test_posts_detail_page_show_correct_context(self):
        """Адрес posts:post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        first_post_object = response.context['post']
        post_author_0 = first_post_object.author
        post_group_0 = first_post_object.group
        post_text_0 = first_post_object.text
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)
        self.assertEqual(post_text_0, PostPagesTests.post.text)

    def test_posts_create_form_show_correct_context(self):
        """Шаблон posts:post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = PostPagesTests.form_fields
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_edit_form_show_correct_context(self):
        """Шаблон posts:post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        form_fields = PostPagesTests.form_fields
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):
        """Первая страница posts:index содержит 10 постов"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Вторая страница posts:index содержит 5 постов"""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_first_page_group_list_contains_ten_records(self):
        """Первая страница posts:group_list содержит 10 постов"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'cats'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list_contains_ten_records(self):
        """Вторая страница posts:group_list содержит 5 постов"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'cats'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_first_page_profile_contains_ten_records(self):
        """Первая страница posts:profile содержит 10 постов"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'test-user'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_ten_records(self):
        """Вторая страница posts:profile содержит 4 поста"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': 'test-user'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_post_create_page_add_post_at_home_page(self):
        """При создании поста, этот пост появляется на главной странице"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostPagesTests.group.pk,
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
                group=PostPagesTests.group,
            ).exists()
        )

    def test_authorized_user_can_follow_and_delete_users(self):
        """Новая запись пользователя появляется в ленте тех, кто
        на него подписан и не появляется в ленте тех, кто не подписан"""
        response = self.authorized_client_2.get(reverse('posts:follow_index'))
        first_post_object = response.context['page_obj'][0]
        self.assertEqual(self.another_post, first_post_object)
        self.assertNotEqual(self.post_2, first_post_object)

    def test_post_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей"""
        response = self.authorized_client_2.get(reverse(
            'posts:profile_follow', args=('test_2-user',)))
        self.assertTrue(
            Follow.objects.filter(
                user=self.another_user,
                author=self.user_2,
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=('test_2-user',)))

    def test_post_unfollow(self):
        """Авторизованный пользователь может удалять из подписок
        других пользователей"""
        response = self.authorized_client_2.get(reverse(
            'posts:profile_unfollow', args=('test_2-user',)))
        self.assertFalse(
            Follow.objects.filter(
                user=self.another_user,
                author=self.user_2,
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=('test_2-user',)))
