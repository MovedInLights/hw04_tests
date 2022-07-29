# # tests/models.py
# # Добавьте в классы Post и Group метод __str__ (если его ещё нет):
# # для класса Post — первые пятнадцать символов поста: **post.text[:15];
# # для класса Group — название группы.

from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

        def test_models_have_correct_object_names(self):
            group = PostModelTest.group
            expected_object_name = group.title
            self.assertEqual(expected_object_name, str(group))

            post = PostModelTest.post
            expected_object_name = post.text
            self.assertEqual(expected_object_name, str(post))
