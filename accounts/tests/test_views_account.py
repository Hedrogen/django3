from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blog.models import Post


class AccountsTest(TestCase):

    def setUp(self):

        post_author = User.objects.create_user(username='test_user', password='pass')
        Post.objects.create(title='TestPost', author=post_author, body='Post body', status='published')
        Post.objects.create(title='TestPost', author=post_author, body='Po23st body', status='published')
        Post.objects.create(title='TestPost3', author=post_author, body='Pos4t body', status='published')

    def test_login(self):

        get_response = self.client.get(reverse('accounts:login'))
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(reverse('accounts:login'), {'username': 'test_user', 'password': 'pass'})
        self.assertEqual(post_response.status_code, 302)

    def test_profile(self):

        # Отправка запросов без авторизации.

        user = User.objects.get(username='test_user')

        get_response = self.client.get(reverse('accounts:account'))
        self.assertEqual(get_response.status_code, 404)

        post_response = self.client.post(reverse('accounts:account'))
        self.assertEqual(post_response.status_code, 404)

        # Отправка запросов с авторизацией.

        login = self.client.login(username='test_user', password='pass')

        get_response = self.client.get(reverse('accounts:account'))
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(reverse('accounts:account'))
        self.assertEqual(post_response.status_code, 200)
