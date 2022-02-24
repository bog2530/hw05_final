from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post, User
from ..views import LIMIT

POSTS = 13


class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='test_group_2',
            slug='test_slug_2',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug},
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': cls.user.username},
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id},
            ): 'posts/post_detail.html',
            reverse(
                'posts:edit', kwargs={'post_id': cls.post.id},
            ): 'posts/create_post.html',
            reverse('posts:create'): 'posts/create_post.html',
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTest.user)

    def test_post_pages_uses_correct_template(self):
        "View-функции используют правильные html-шаблоны"
        for reverse_name, template in (
            PostsViewsTest.templates_pages_names.items()
        ):
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_group_lis_profile_correct_context(self):
        "Проверка Context в index, group_list, profile"
        templates_pages_obj = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug},
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username},
            ): 'posts/profile.html',
        }
        for url in templates_pages_obj:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn('page_obj', response.context)
                post_image = response.context['page_obj'][0].image
                post_text = response.context['page_obj'][0].text
                self.assertEqual(post_image, PostsViewsTest.post.image)
                self.assertEqual(post_text, PostsViewsTest.post.text)

    def test_post_post_detail_page_show_correct_context(self):
        "Проверка Context в post_detail"
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertIn('post', response.context)
        post_text = response.context['post'].text
        post_image = response.context['post'].image
        self.assertEqual(post_text, PostsViewsTest.post.text)
        self.assertEqual(post_image, PostsViewsTest.post.image)

    def test_post_create_edit_page_show_correct_contex(self):
        "Проверка Context в create и edit"
        templates_pages_obj = {
            reverse(
                'posts:edit', kwargs={'post_id': self.post.id},
            ): 'posts/create_post.html',
            reverse('posts:create'): 'posts/create_post.html',
        }
        for url in templates_pages_obj:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn('form', response.context)
                form = response.context.get('form')
                self.assertIsInstance(form, PostForm)

    def test_post_right_group(self):
        "Проверка правильной группы поста"
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug}))
        self.assertIn('page_obj', response.context)
        post_text = len(response.context['page_obj'])
        self.assertEqual(post_text, 0)

    def test_cache(self):
        "Тестирование кеша страницы index"
        response = self.authorized_client.get('posts:index')
        content = response.content
        Post.objects.all().delete()
        response = self.authorized_client.get('posts:index')
        self.assertEqual(response.content, content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = [Post(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        ) for i in range(POSTS)]
        Post.objects.bulk_create(cls.post)

        cls.page_1 = LIMIT
        cls.page_2 = POSTS - LIMIT
        cls.paginator_context = {
            reverse('posts:index'): cls.page_1,
            reverse('posts:index') + '?page=2': cls.page_2,
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}):
                cls.page_1,
            reverse('posts:group_list',
                    kwargs={'slug': cls.group.slug}) + '?page=2': cls.page_2,
            reverse('posts:profile', kwargs={'username': cls.user}):
                cls.page_1,
            reverse('posts:profile',
                    kwargs={'username': cls.user}) + '?page=2':
                cls.page_2,
        }

    def setUp(self):
        self.guest_client = Client()

    def test_page_contains_ten_records(self):
        "Тестирование паджинатора"
        for request_page, page in self.paginator_context.items():
            with self.subTest(requested_page=request_page):
                response = self.guest_client.get(request_page)
                self.assertEqual(len(response.context['page_obj']), page)


class FollowingViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='author_1')
        cls.user_2 = User.objects.create_user(username='author_2')
        cls.post = Post.objects.create(
            author=cls.user_2,
            text='Тестовый текст',
        )

    def setUp(self):
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(FollowingViewsTest.user_1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(FollowingViewsTest.user_2)

    def test_follow(self):
        "Тест подписки пользователя"
        self.authorized_client_1.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username}),
        )
        follower = Follow.objects.latest('id')
        user_following_count = self.user_1.follower.count()
        self.assertEqual(user_following_count, 1)
        self.assertEqual(self.user_1.id, follower.user.id)
        self.assertEqual(self.user_2.id, follower.author.id)
        self.authorized_client_1.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_2.username}),
        )
        user_unfollowing_count = self.user_1.follower.count()
        self.assertEqual(user_unfollowing_count, 0)

    def test_folowing_post(self):
        "Тест ленты подписок"
        self.authorized_client_1.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username}),
        )
        response = self.authorized_client_1.get(
            reverse('posts:follow_index'),
        )
        self.assertIn('page_obj', response.context)
        post_text = response.context['page_obj'][0].text
        self.assertEqual(post_text, FollowingViewsTest.post.text)
        self.assertTemplateUsed(response, 'posts/follow.html')

    def test_not_folowing_post(self):
        "Тест ленты подписок не подписанного пользователя"
        self.authorized_client_1.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username}),
        )
        response = self.authorized_client_2.get(
            reverse('posts:follow_index'),
        )
        self.assertIn('page_obj', response.context)
        context = response.context.get('page_obj')
        self.assertNotIn(FollowingViewsTest.post, context)
