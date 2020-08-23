from django.test import TestCase
from datetime import time
from django.contrib.auth.models import User

from blog.models import Post
from blog.forms import CommentForm


class BlogFormsTest(TestCase):

    def setUp(self):
        author = User.objects.create_user(username='test_user', password='pass')
        post = Post.objects.create(title='Forms_test_title', body='test_body', tags='test', author=author)

    def test_create(self):

        author = User.objects.get(username='test_user')

        comment = CommentForm()
        self.assertFalse(comment.is_valid())

        comment = CommentForm({'user': author})
        self.assertFalse(comment.is_valid())

        comment = CommentForm({'body': '', 'user': author})
        self.assertFalse(comment.is_valid())

        comment = CommentForm({'user': author, 'body': 'test_body'})
        self.assertTrue(comment.is_valid())
