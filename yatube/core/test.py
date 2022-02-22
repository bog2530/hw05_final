from django.test import Client, TestCase


class CoreViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_post_pages_uses_correct_template(self):
        "View-функция используют правильные html-шаблоны"
        response = self.guest_client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
