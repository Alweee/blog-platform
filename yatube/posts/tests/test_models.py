from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост из пятнадцати символов',
        )
        cls.task = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def test_models_have_correct_str_(self):
        post = self.post
        group = self.group
        object_field = {
            post: post.text,
            group: group.title,
        }
        for model, field in object_field.items():
            with self.subTest(model=model):
                self.assertEqual(str(model), field)

    def test_verbose_name_in_post_correct(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        task = PostModelTest.task
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата и время публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        task = PostModelTest.task
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, expected_value)

    def test_group_title(self):
        """title для модели Group совпадает с ожидаемым."""
        group = Group.objects.get(pk=1)
        self.assertEqual(group.title, 'Тестовая группа')

    def test_posts_text_have_15_char(self):
        """test text для модели Post утверждаем, что упадёт."""
        post = PostModelTest.post
        self.assertEqual(post.text[:15], 'Тестовый пост и')
