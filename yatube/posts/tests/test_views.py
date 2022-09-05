import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow

TEST_OF_PAGI_1: int = 10
TEST_OF_PAGI_2: int = 3
User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        cls.posts = [
            Post(
                author=cls.author,
                text='test_post',
                group=cls.group,
            ) for i in range(1, 14)
        ]
        Post.objects.bulk_create(cls.posts)

        cls.templates = {
            1: reverse('posts:index'),
            2: reverse('posts:group_list',
                       kwargs={'slug': f'{cls.group.slug}'}),
            3: reverse('posts:profile',
                       kwargs={'username': f'{cls.author.username}'})
        }

    def test_first_page_contains_ten_records(self):
        for i in PaginatorViewsTest.templates.keys():
            with self.subTest(i=i):
                response = self.client.get(self.templates[i])
                self.assertEqual(len(response.context.get(
                    'page_obj'
                ).object_list), TEST_OF_PAGI_1)

    def test_second_page_contains_three_records(self):
        for i in PaginatorViewsTest.templates.keys():
            with self.subTest(i=i):
                response = self.client.get(self.templates[i] + '?page=2')
                self.assertEqual(len(response.context.get(
                    'page_obj'
                ).object_list), TEST_OF_PAGI_2)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='test_author'
        )
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)
        cls.not_author = User.objects.create_user(
            username='test_not_author'
        )
        cls.authorized_not_author_client = Client()
        cls.authorized_not_author_client.force_login(cls.not_author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
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
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author,
            image=uploaded,
        )
        cls.templ_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug':
                    f'{cls.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username':
                    f'{cls.author.username}'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id':
                    f'{cls.post.id}'}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{cls.post.id}'}): 'posts/create_post.html',
        }

        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.image, self.post.image)

    def test_page_uses_correct_template(self):
        for reverse_name, template in PostsPagesTests.templ_names.items():
            with self.subTest(template=template):
                response = PostsPagesTests.auth_author_client.get(
                    reverse_name
                )
                self.assertTemplateUsed(response, template)

    def test_post_create_correct_context(self):
        response = PostsPagesTests.auth_author_client.get(
            reverse('posts:post_create')
        )
        for value, expected in PostsPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        response = PostsPagesTests.auth_author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'})
        )
        for value, expected in PostsPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_correct_context(self):
        response = PostsPagesTests.auth_author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_index_show_correct_context(self):
        response = self.auth_author_client.get(reverse('posts:index'))
        self.post_info(response.context['page_obj'][0])

    #def test_profile_show_correct_context(self):
    #    response = self.auth_author_client.get(reverse('posts:profile', kwargs={'username': f'{self.author.username}'}))
    #    self.post_info(response.context['page_obj'][0])
    #    self.assertEqual(response.context['author'], self.user)

    def test_post_detail_show_correct_context(self):
        response = self.auth_author_client.get(reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'}))
        self.post_info(response.context['post'])

    def test_group_post_show_correct_context(self):
        response = self.auth_author_client.get(reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        self.post_info(response.context['page_obj'][0])
        self.assertEqual(response.context['group'], self.group)