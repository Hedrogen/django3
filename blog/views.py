from taggit.models import Tag
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, View
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from .forms import EmailPostForm, CommentForm, SearchForm, PostForm, CommentRatingForm
from .models import Post, Comment, CommentRating
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse

import logging


logger = logging.getLogger('blog_views')

# отображение списка статей


def post_list(request, tag_slug=None):

    object_list = Post.published.all()

    tag = None
    tags = Post.tags.all()

    paginate_number = 3

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, paginate_number)
    page = request.GET.get('page')

    logger.info('Отображение списка постов')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts, 'page': page, 'tag': tag, 'tags': tags})


# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_search(request):

    """ Функция поиска постов по содержанию тела поста и загаловку статьи"""

    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(
                search=search_vector,
                similitiry=TrigramSimilarity('title', query),
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3).order_by('-similitiry')
            # results = Post.objects.annotate(
            #     similarity=TrigramSimilarity('title', query),
            # ).filter(similarity__gt=0.3).order_by('-similarity')
    logger.info('Поиск постов')
    return render(request, 'blog/post/search.html', {'form_search': form, 'query': query, 'results': results})


def post_detail(request, year, month, day, post):

    """ Детальное отображение поста """

    post = get_object_or_404(Post,
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(activate=True)
    images = post.images.all()

    new_comment = None

    try:
        if request.method == 'POST':
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                comment_form = comment_form.save(commit=False)
                comment_form.post = post
                logger.info('Добавление комментария')
                comment_form.user = request.user
                comment_form.save()
        else:
            logger.info('Загрузка формы комментария')
            comment_form = CommentForm()
    except ValueError:
        return HttpResponse('Only authorized users can add comments', status=403)

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'images': images,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


def post_share(request, post_id):

    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading " {} "'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'gitaglotus@gmail.com', [cd['to']])
            # send_mail(subject, message, 'admin@blog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


class PostCreate(View):

    """ Отвечает за создание поста """

    def get(self, request):
        logger.info('Отображение формы поста')
        post_form = PostForm(request.POST)
        return render(request, 'blog/create/post_create.html', {'post_form': post_form})

    def post(self, request):
        try:
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                post_form.save(commit=False)
                post_form.instance.author = request.user
                post_form.save()
                logger.info('Cоздание поста')
                return render(request, 'blog/create/post_success_created.html')
        except ValueError:
            return HttpResponse('You don\'t have permissions make this', status=403)


class PostEdit(View):

    """ Отвечает за измение постов """

    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        post_form = PostForm(instance=post)
        return render(request, 'blog/post/post_edit.html', {'post_form': post_form, 'post': post})

    def post(self, request, slug):

        post = Post.objects.get(slug=slug)
        post_form = PostForm(request.POST, instance=post)
        author = post.author

        if post_form.is_valid():
            if request.user == post.author or request.user.is_staff:
                post_form.save(commit=False)
                logger.info('Обновление поста')
                post_form.instance.author = author
                post_form.save()
                return redirect(post)
            else:
                return HttpResponse(status=403)
        return render(request, 'blog/post/post_edit.html', {'post_form': post_form, 'post': post})


class PostDelete(View):

    """ Отвечает за удаление поста """

    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        if request.user == post.author or request.user.is_staff:
            return render(request, 'blog/post/post_delete.html', {'post': post})
        return redirect('blog:post_list')

    def post(self, request, slug):
        post = Post.objects.get(slug=slug)
        if request.user == post.author or request.user.is_staff:
            post.delete()
            return redirect('blog:post_list')
        else:
            return HttpResponse('You don\'t have permissions make this', status=403)
