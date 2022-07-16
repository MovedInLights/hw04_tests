# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group
from http import HTTPStatus
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        # Создаем экземпляр клиента
        guest_client = Client()
        # Делаем запрос к главной странице и проверяем статус
        response = guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.not_author = User.objects.create_user(username='not_Author')

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
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(cls.not_author)

    def test_urls_all_users(self):
        """URL-адрес доступен для всех пользователей."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.author}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = Client().get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_page_does_not_exist(self):
        """URL-адрес не существует."""
        templates_url_names = {
            'unexisting_page.html': '/unexisting_page',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_create_post_authorized(self):
        """URL-адрес доступен для авторизированных пользователей."""
        templates_url_names = {
            'posts/create_post.html': '/create/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_edit_post_authorized_author(self):
        """URL-для редактирования доступен для авторизированных юзеров."""
        response = self.authorized_client.get(
            reverse('posts:post_create',)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_edit_authorized_not_author_redirection(self):
        """URL-адрес переадресует не автора при запросе на редактирование."""
        response = Client().post(
            reverse('posts:post_edit', kwargs={'post_id': '1'},)
        )
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
