from http import HTTPStatus

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
        for link in self.templates_url_names:
            with self.subTest():
                response = self.guest_client.get(link)
                self.assertEqual(response.status_code, HTTPStatus.OK)
