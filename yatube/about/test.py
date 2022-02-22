from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_about = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_urls_about(self):
        for url in self.url_about:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_about_correct_template(self):
        for url, template in self.url_about.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
