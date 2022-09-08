from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostGroupModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Special test text more 15',
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_post_str(self):
        """Проверка строкового представления для для post и group"""
        self.assertEqual(self.post.text[:15], str(self.post))
        self.assertEqual(self.group.title, str(self.group))

    def test_verbose_name_post(self):
        """Verbose_name в полях post совпадает с ожиданиями"""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = self.post._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_post_help_text(self):
        """Проверка help_text у post."""
        feild_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой относится пост', }
        for value, expected in feild_help_texts.items():
            with self.subTest(value=value):
                help_text = self.post._meta.get_field(value).help_text
                self.assertEqual(help_text, expected)

    def test_verbose_name_group(self):
        """Verbose_name в полях совпадает group с ожиданиями"""
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'slug',
            'description': 'Описание'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = self.group._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='auth1')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.follow = Follow.objects.create(
            user=cls.user1,
            author=cls.user2,
        )

    def test_follow_str(self):
        """Проверка строкового представления в follow"""
        self.assertEqual(
            f'{self.follow.user} подписался на {self.follow.author}',
            str(self.follow)
        )

    def test_follow_verbose_name(self):
        """Verbose_name в полях follow совпадает с ожиданием"""
        field_verboses = {
            'user': 'Пользователь',
            'author': 'Автор'
        }
        for value, expected in field_verboses.items():
            with self.subTest(valuse=value):
                verbose_name = self.follow._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='_text',
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            text='comment_text',
            author=cls.user,
            post=cls.post
        )

    def test_comment_str(self):
        """Проверка строкового представления в comment"""
        self.assertEqual(self.comment.text[:15], str(self.comment))

    def test_comment_verbose_name(self):
        """Verbose_name в полях comment совпадает с ожиданием"""
        field_verboses = {
            'post': 'post',
            'text': 'Текст комментария',
            'created': 'Дата комментария'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = self.comment._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)
