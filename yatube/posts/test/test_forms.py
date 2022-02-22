from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post, User


class PostFormTest(TestCase):
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
            description='Тестовое описание_2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        "Отправка формы со страницы create"
        count = Post.objects.count()
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
            content_type='image/gif',
        )
        form_data = {
            'text': 'тест',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True,
        )
        new_post = Post.objects.latest('pub_date')
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.post.author}),
        )
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group, form_data['group'])
        self.assertEqual(new_post.image, form_data['image'])
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        "Редактирование формы на странице edit"
        count = Post.objects.count()
        form_data = {
            'text': '12345',
            'group': self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse('posts:edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        edit_post = Post.objects.latest('pub_date')
        self.assertEqual(Post.objects.count(), count)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group.id, form_data['group'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.post(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        )
        post_text = len(response.context['page_obj'])
        self.assertEqual(post_text, 0)

    def test_create_new_post(self):
        "Отправка формы гостем со страницы create "
        count = Post.objects.count()
        form_data = {
            'text': 'тест_2',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), count)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/create/'),
        )

    def test_comment_post(self):
        "Отправка формы add_comment авторизированным пользователем"
        count = Comment.objects.count()
        form_data = {
            'text': 'Тест',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        comment = self.post.comments.all()[0]
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(Comment.objects.count(), count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comment_guest_client_post(self):
        "Отправка формы add_comment гостем "
        count = Comment.objects.count()
        form_data = {
            'text': 'Тест',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), count)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/posts/1/comment/'),
        )
