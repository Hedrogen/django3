from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from blog.models import Post


class PostsListTest(TestCase):

    def setUp(self) -> None:
        post_author = User.objects.create_user(username='new_user', password='pass')
        Post.objects.create(title='TestPost', author=post_author, body='Post body', status='published')
        Post.objects.create(title='TestPost', author=post_author, body='Po23st body', status='published')
        Post.objects.create(title='TestPost3', author=post_author, body='Pos4t body', status='published')

    def test_url_unique(self):
        test_post1 = Post.objects.get(body__startswith='Post body')
        test_post2 = Post.objects.get(body__startswith='Po23st body')
        test1_post_absolute_url = test_post1.get_absolute_url()
        test2_post_absolute_url = test_post2.get_absolute_url()
        self.assertNotEqual(test1_post_absolute_url, test2_post_absolute_url)

    def test_slug_unique(self):
        test_post1 = Post.objects.get(body__startswith='Post body')
        test_post2 = Post.objects.get(body__startswith='Po23st body')
        test1_slug = test_post1.slug
        test2_slug = test_post2.slug
        self.assertNotEqual(test1_slug, test2_slug)
