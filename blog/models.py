from taggit.managers import TaggableManager
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse
from time import time
from django.conf import settings
from ckeditor_uploader.fields import RichTextUploadingField


def make_slug(st):

    new_slug = slugify(st) + '-' + str(int(time()))
    return new_slug


class PublishManager(models.Manager):
    def get_queryset(self):
        return super(PublishManager, self).get_queryset().filter(status='published')


class Post(models.Model):

    """ Модель поста """

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', blank=True)
    # author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    # body = models.TextField()
    body = RichTextUploadingField(blank=True, null=True)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    tags = TaggableManager()        # tag

    objects = models.Manager()       # Менеджер обьектов по умолчанию
    published = PublishManager()    # Пользовательский менеджер обьектов

    class Meta:
        ordering = ('-publish',)

    def save(self, *args, **kwargs):
        if not self.id:
            self.status = 'published'
            self.slug = make_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])


class Comment(models.Model):

    """ Модель комментария """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)  # В будущем надо будет убрать
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment', blank=True, null=True)
    email = models.EmailField()
    body = models.TextField(max_length=15000)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    activate = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)


class CommentRating(models.Model):

    """ Модель рейтинга комментария """

    # ip = models.CharField('IP', max_length=15)
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name='comment_rating')
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.comment} - rating: {self.rating}"


class Images(models.Model):

    """ Модель изображения/изображений поста """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True)
    upload_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('upload_time',)

    def __str__(self):
        return 'Post: {}, Upload_time: {}, Title: {}'.format(self.post, self.upload_time, self.title)