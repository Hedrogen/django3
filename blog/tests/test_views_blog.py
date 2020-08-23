from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.urls import reverse

from blog.models import Post
from blog.views import post_list


class PostsViewsTest(TestCase):

    def setUp(self):

        """ Создает тестовые данные """

        post_author = User.objects.create_user(username='test_user', password='pass')
        no_author_of_the_post = User.objects.create_user(username='l_user', password='pass')
        Post.objects.create(title='TestPost', author=post_author, body='Post body', status='published')
        Post.objects.create(title='TestPost', author=post_author, body='Po23st body', status='published')
        Post.objects.create(title='TestPost3', author=post_author, body='Pos4t body', status='published')

    def test_list_http_response(self):

        response = self.client.get(reverse('blog:post_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post/list.html')
        self.assertTrue('posts' in response.context)

    def test_detail_http_response(self):

        test_post = Post.objects.get(body__startswith='Post body')
        test_post_url = test_post.get_absolute_url()
        response = self.client.get(test_post_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post/detail.html')

    def test_comment_add_http_response(self):

        test_post = Post.objects.get(body__startswith='Post body')
        test_post_url = test_post.get_absolute_url()
        #  Добавление комментария без авторизации. Ожидается ошибка 403

        post_response_0 = self.client.post(test_post_url, {'body': 'test_comment'})
        self.assertEqual(post_response_0.status_code, 403)

        # Доавление комментария с авторизацией

        login = self.client.login(username='test_user', password='pass')

        post_response_1 = self.client.post(test_post_url, {'body': 'test_comment_success'})
        self.assertEqual(post_response_1.status_code, 200)

    def test_post_create_http_response(self):

        # Создание поста без авторизации. Ожидается ошибка 403

        test_creating_a_post_without_authorization = self.client.post(
            reverse('blog:post_create_url'),
            {'title': 'test', 'body': 'test', 'tags': 'test'}
        )
        self.assertEqual(test_creating_a_post_without_authorization.status_code, 403)

        # Создание поста с авторизацией

        login = self.client.login(username='test_user', password='pass')

        get_response = self.client.get(reverse('blog:post_create_url'))
        self.assertEqual(str(get_response.context['user']), 'test_user')
        self.assertEqual(get_response.status_code, 200)

        test_post_create = self.client.post(
            reverse('blog:post_create_url'),
            {'title': 'test_title', 'body': 'some_test_text', 'tags': 'test_tag'})
        self.assertEqual(test_post_create.status_code, 200)

    def test_post_delete(self):

        first_post = Post.objects.get(body='Post body')
        second_post = Post.objects.get(body='Po23st body')

        oppressed_post = first_post

        # Удаление поста дез авторизации. Ожидается ошибка 403.

        post_response = self.client.post('/blog/post/delete/' + oppressed_post.slug)
        self.assertEqual(post_response.status_code, 403)

        # Удаление поста автором.

        login = self.client.login(username='test_user', password='pass')
        post_response = self.client.post('/blog/post/delete/' + oppressed_post.slug)
        self.assertEqual(post_response.status_code, 302)

        self.client.logout()

        oppressed_post = second_post

        # Удаление поста авторизованным левым пользователем. Ожидается ошибка 403

        login = self.client.login(username='l_user', password='pass')
        post_response = self.client.post('/blog/post/delete/' + oppressed_post.slug)
        self.assertEqual(post_response.status_code, 403)
