from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_1,
            text='Тестовый текст',
        )
        cls.url_guest_client = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user_1}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
        }
        cls.url_authorized_client = {
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(StaticURLTests.user_1)
        self.user_2 = User.objects.create_user(username='author_2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_urls_guest_client(self):
        "Доступность страниц для гостя"
        for url in self.url_guest_client:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_not_found(self):
        "Запрос к несуществующей странице"
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_authorized_client(self):
        "Доступность страниц для авторизованного клиента"
        for url in self.url_authorized_client:
            with self.subTest(url=url):
                response = self.authorized_client_1.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_client_not_author_redirects(self):
        "Недоступность edit для для стороннего пользователя"
        response = self.authorized_client_2.get(
            f'/posts/{self.post.id}/edit/', follow=True,
        )
        self.assertRedirects(
            response, (f'/posts/{self.post.id}/'))

    def test_urls_guest_client_redirects(self):
        "Перенаправление на страницу входа"
        for url in self.url_authorized_client:
            with self.subTest(url=url):
                response = self.guest_client.get(
                    url, follow=True,
                )
                self.assertRedirects(
                    response, (f'/auth/login/?next={url}'))

    def test_urls_authorized_client_correct_template(self):
        "Проверка вызываемых HTML-шаблонов для гостя"
        for url, template in self.url_authorized_client.items():
            with self.subTest(url=url):
                response = self.authorized_client_1.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_guest_client_correct_template(self):
        "Проверка вызываемых HTML-шаблонов авторизованного клиента"
        for url, template in self.url_guest_client.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
