import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Новый пользователь')
        cls.comment_author = User.objects.create_user(
            username='Автор комментария',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.auth_user_comment = Client()
        self.auth_user_comment.force_login(self.comment_author)

    def test_posts_forms_create_post(self):
        """Проверка, создает ли форма пост в базе."""
        post_count = Post.objects.count()
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
            'text': 'Тестовый пост формы',
            'group': self.group.id,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

        last_post = Post.objects.first()
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.author)
        self.assertEqual(last_post.group.id, form_data['group'])
        self.assertEqual(last_post.image.name, 'posts/small.gif')

    def test_authorized_client_create_comment(self):
        """Проверка создания комментария авторизированным пользователем."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Тестовый комментарий'}
        response = self.auth_user_comment.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True,
        )
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.comment_author)
        self.assertEqual(comment.post_id, self.post.id)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )

    def test_not_authorized_client_create_comment(self):
        """Проверка создания комментария не авторизированным пользователем."""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text='Текст поста для комментирования',
            author=self.author,
        )
        form_data = {'text': 'Тестовый комментарий'}
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_posts_forms_edit_post(self):
        """Проверка, редактируется ли пост."""
        form_data = {
            'text': 'Новый текст поста',
            'group': self.group.id,
        }
        self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id},
        ), data=form_data)

        edit_post = Post.objects.get(id=self.post.id)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group.id, form_data['group'])

    def test_groups_forms_edit_post(self):
        """Проверка, редактируется ли группа."""
        form_data = {
            'title': 'Новое название группы',
            'description': 'Новое описание группы',
            'slug': 'test_slug',
            'group': self.group.id,
        }
        self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id},
        ), data=form_data)

        edit_post = Post.objects.get(id=self.post.id)
        self.assertEqual(edit_post.group.id, form_data['group'])
