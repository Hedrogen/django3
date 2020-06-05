from django.utils.safestring import mark_safe
from django import template
from . .models import Post
import markdown


register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/all_tags.html')
def all_tags():
    tags = Post.tags.all()
    return {'tags': tags}


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=2):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

# @register.inclusion_tag('blog/post/sidebar_search.html')
# def post_search():
