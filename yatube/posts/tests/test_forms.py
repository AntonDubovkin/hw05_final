import tempfile
import shutil

from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем юзера
        cls.post_author = User.objects.create_user(
            username='post_author'
        )
        cls.comm_author = User.objects.create_user(
            username='comm_author'
        )
        cls.group_old = Group.objects.create(
            title='Test_title_old',
            slug='test-slug_old',
            description='Test_description_old'
        )
        cls.group_new = Group.objects.create(
            title='Test_title_new',
            slug='test-slug_new',
            description='Test_description_new'
        )

    def setUp(self):
        # создаем гостевого юзера
        self.guest_user = Client()
        # создаем авторизованного автора поста
        self.authorized_user = Client()
        # авторизуем
        self.authorized_user.force_login(self.post_author)
        # Создаём авторизованного комментатора
        self.auth_user_comm = Client()
        self.auth_user_comm.force_login(self.comm_author)

    @classmethod
    def tearDownClass(cls):
        """Очищаем кэш"""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Проверка создания поста"""
        count_posts = Post.objects.count()
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
            'text': 'form_text',
            'group': self.group_old.id,
            'image': uploaded,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post_author.username}))
        self.assertEqual(Post.objects.count(), count_posts + 1)
        post = Post.objects.latest('id')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.image.name, 'posts/small.gif')
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group_id, form_data['group'])

    def test_authorized_user_create_comment(self):
        """Проверка создания поста авторизованным юзером"""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text='comment_text',
            author=self.post_author
        )
        form_data = {'text': 'test comment'}
        response = self.auth_user_comm.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.latest('id')
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.comm_author)
        self.assertEqual(comment.post_id, post.id)
        self.assertRedirects(
            response, reverse('posts:post_detail', args={post.id})
        )

    def test_nonauthorized_user_create_comment(self):
        """Проверка создания поста не авторизованным юзером"""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text='comment_text',
            author=self.post_author
        )
        form_data = {'text': 'test comment'}
        response = self.guest_user.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        redirect = reverse('login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': post.id}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(response, redirect)

    def test_authorized_user_edit_post(self):
        """Проверка редактирования поста авторизованным юзером"""
        post = Post.objects.create(
            text='post_text',
            author=self.post_author,
            group=self.group_old
        )
        form_data = {
            'text': 'post_text_edit',
            'group': self.group_new.id
        }
        response = self.authorized_user.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        post_one = Post.objects.latest('id')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_one.text, form_data['text'])
        self.assertEqual(post_one.author, self.post_author)
        self.assertEqual(post_one.group_id, form_data['group'])
        self.assertFalse(
            Post.objects.filter(
                group=self.group_old.id,
                text='post_text',
            ).exists()
        )

    def test_nonauthorized_user_create_post(self):
        """Проверка создания поста неавторизованным юзером"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'non_auth_edit_text',
            'group': self.group_old.id
        }
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)
