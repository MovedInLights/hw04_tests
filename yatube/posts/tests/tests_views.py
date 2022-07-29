# tests/tests_views.py

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
            pub_date='14.07.2022',
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:posts_list'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test_slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'author'})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:posts_list'))
        first_object = response.context['page_obj'][0]
        first_object_text = first_object.text
        self.assertEqual(first_object_text, 'Тестовый текст')

    def test_group_list_page_show_correct_context(self):
        """Шаблон list_page сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        )
        self.assertEqual(
            response.context.get('group').title, 'Тестовая группа'
        )
        self.assertEqual(
            response.context.get('group').description, 'Тестовое описание'
        )

    def test_profile_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get
                    (reverse('posts:profile', kwargs={'username': 'author'})))
        first_object = response.context['page_obj'][0]
        first_object_author = first_object.author.username
        self.assertEqual(first_object_author, 'author')

    def test_group_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail', kwargs={'post_id': '1'})))
        first_object = response.context['post']
        first_object_text = first_object.text
        self.assertEqual(first_object_text, 'Тестовый текст')

    def test_crete_post_show_correct_context(self):
        """Шаблон crete_post сформирован с правильной формой."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Шаблон edit_post сформирован с правильной формой."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'},)
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_new_post(self):
        """Шаблон index показывает созданный пост."""
        response = self.authorized_client.get(reverse('posts:posts_list'))
        first_object = response.context['page_obj'][0]
        first_object_author = first_object.author.username
        first_object_group = first_object.group.title
        first_object_text = first_object.text
        self.assertEqual(first_object_author, 'author')
        self.assertEqual(first_object_group, 'Тестовая группа')
        self.assertEqual(first_object_text, 'Тестовый текст')

    def test_group_page_show_new_post(self):
        """Шаблон index показывает созданный пост."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'})
        )
        first_object = response.context['page_obj'][0]
        first_object_author = first_object.author.username
        first_object_group = first_object.group.title
        first_object_text = first_object.text
        self.assertEqual(first_object_author, 'author')
        self.assertEqual(first_object_group, 'Тестовая группа')
        self.assertEqual(first_object_text, 'Тестовый текст')

    def test_profile_show_new_post(self):
        """Шаблон index показывает созданный пост."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'author'})
        )
        first_object = response.context['page_obj'][0]
        first_object_author = first_object.author.username
        first_object_group = first_object.group.title
        first_object_text = first_object.text
        self.assertEqual(first_object_author, 'author')
        self.assertEqual(first_object_group, 'Тестовая группа')
        self.assertEqual(first_object_text, 'Тестовый текст')


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        bulk_post = []
        for i in range(0, 13):
            bulk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=cls.group,
                                  author=cls.author))
        Post.objects.bulk_create(bulk_post)

    def test_first_page_index_ten_records(self):
        response = self.client.get(reverse('posts:posts_list'))
        # Проверка: количество постов на первой posts_list странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_three_records(self):
        # Проверка: на второй posts_list странице должно быть три поста.
        response = self.client.get(reverse('posts:posts_list') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_ten_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
        )
        # Проверка: количество постов на первой странице group_list равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_three_records(self):
        # Проверка: на второй странице group_list должно быть три поста.
        response = self.client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_author_ten_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'author'})
        )
        # Проверка: количество постов на первой странице group_list равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_author_three_records(self):
        # Проверка: на второй странице group_list должно быть три поста.
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={'username': 'author'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
