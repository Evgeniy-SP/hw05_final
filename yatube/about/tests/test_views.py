from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.templates_url_names = [
            reverse('about:author'),
            reverse('about:tech'),
        ]

    def test_about_pages_are_names(self):
        """Проверка ожидаемых ссылок."""
        for name, url in (
            ('about:author', '/about/author/'),
            ('about:tech', '/about/tech/'),
        ):
            self.assertEqual(reverse(name), url)
