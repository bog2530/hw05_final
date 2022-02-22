from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа 1234567890',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст 0987654321',
        )

    def test_models_have_correct_object_names(self):
        "Тестирование моделей"
        post_test = {
            PostModelTest.post: self.post.text[:15],
            PostModelTest.group: self.group.title,
        }
        for value, cut in post_test.items():
            with self.subTest():
                self.assertEqual(str(value), cut)
