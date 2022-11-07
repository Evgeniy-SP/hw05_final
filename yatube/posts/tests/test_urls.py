from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='slug',
            description='Тестовое описание',
        )
        cls.author = User.objects.create_user(username='test_user')
        cls.no_author = User.objects.create_user(
            username='not_auth_user'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.templates_url_names_public = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug},
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': cls.author.username},
            ),
        }

        cls.templates_url_names_private = {
            'posts/post_create.html': reverse('posts:post_create')
        }
        cls.templates_url_authorised = {
            reverse(
                'posts:index'
            ): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'bad_slug'}
            ): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': cls.author.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_create'
            ): HTTPStatus.OK,
            '/bad_link/': HTTPStatus.NOT_FOUND,
        }

        cls.templates_url_unauthorised = {
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': cls.group.slug
                },
            ): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'bad_slug'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={
                    'username': cls.author.username
                },
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_create'): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id},): HTTPStatus.FOUND,
            '/bad_link/': HTTPStatus.NOT_FOUND,
        }

        cls.templates_url_names_private = {
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'bad_slug'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': cls.author.username}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }

        cls.templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug},
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': cls.author.username},
            ),
            'posts/post_create.html': reverse('posts:post_create'),
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

        self.no_author_client = Client()
        self.no_author_client.force_login(self.no_author)

    def test_urls_guest_user_private(self):
        """
        Проверка на доступность ссылок гостевому пользователю и редирект
        недоступных страниц.
        """
        for url, status_code in self.templates_url_names_private.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_guest_user_private_redirect(self):
        """
        Проверка на доступность ссылок гостевому пользователю и редактирования
        недоступных страниц.
        """
        response = self.guest_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_guest_user_public(self):
        """
        Проверка на доступность ссылок гостевому пользователю и редирект
        доступных страниц.
        """
        for template, reverse_name in self.templates_url_names_public.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_user(self):
        """Проверка ссылок авторизованному пользователю - автору поста."""

        for url, status_code in self.templates_url_authorised.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_no_authorized_user(self):
        """Проверка ссылок авторизованному пользователю - не автору поста."""
        for url, status_code in self.templates_url_unauthorised.items():
            with self.subTest():
                response = self.no_author_client.get(url)
                self.assertEqual(
                    response.status_code,
                    status_code
                )

    def test_urls_use_correct_template(self):
        """Проверка на то что URL-адрес использует подходящий шаблон."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)