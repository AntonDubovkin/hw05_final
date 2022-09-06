from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в БД для проверки доступности
        cls.user_author = User.objects.create_user(username='user_author')
        cls.user_another = User.objects.create_user(username='user_another')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user_author)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user_another)
        cache.clear()

    def test_unauthorized_user_urls_status_code(self):
        """Проверка status_code для неавторизованного пользователя."""
        field_urls_code = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': 'bad_slug'}): HTTPStatus.NOT_FOUND,
            reverse('posts:profile',
                    kwargs={'username': self.user_author}): HTTPStatus.OK,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}): HTTPStatus.FOUND,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_authorized_user_urls_status_code(self):
        """Проверка tatus_code для авторизованного пользователя"""
        field_urls_code = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': 'bad_slug'}): HTTPStatus.NOT_FOUND,
            reverse('posts:profile',
                    kwargs={'username': self.user_author}): HTTPStatus.OK,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}): HTTPStatus.FOUND,
            reverse('posts:post_create'):
                HTTPStatus.OK, '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.authorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_author_urls_status_code(self):
        """Проверка tatus_code для автора"""
        field_urls_code = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': 'bad_slug'}): HTTPStatus.NOT_FOUND,
            reverse('posts:profile',
                    kwargs={'username': self.user_author}): HTTPStatus.OK,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}): HTTPStatus.OK,
            reverse('posts:post_create'):
                HTTPStatus.OK, '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.post_author.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user_author}):
                'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}):
                'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for urls, template in templates_urls_names.items():
            with self.subTest(adress=urls):
                response = self.post_author.get(urls)
                self.assertTemplateUsed(response, template)
