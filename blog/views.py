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


# отображение списка статей


def post_list(request, tag_slug=None):
    object_list = Post.published.all()

    tag = None
    tags = Post.tags.all()

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    # posts = Post.published.all()
    return render(request, 'blog/post/list.html', {'posts': posts, 'page': page, 'tag': tag, 'tags': tags})


# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'

#  Поиск по телу и загаловку статьи


def post_search(request):
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

    return render(request, 'blog/post/search.html', {'form_search': form, 'query': query, 'results': results})


# детальное отображение статьи


def post_detail(request, year, month, day, post):

    post = get_object_or_404(Post,
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(activate=True)
    images = post.images.all()

    new_comment = None

    if request.method == 'POST':
        # comments_rating = CommentRatingForm(data=request.POST)
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
        # if comments_rating.is_valid():
        #     comments_rating.save()
    else:
        comment_form = CommentForm()

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
            # send_mail(subject, message, 'gitaglotus@gmail.com', [cd['to']])
            send_mail(subject, message, 'admin@blog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


'''  Относится к PostCreate
Ничего нихера не создается, нужно как-то передать
параметр user для поля author'''


class PostCreate(View):
    def get(self, request):
        post_form = PostForm(request.POST)
        print('\n\n\n USER[GET]: \n', request.user.id, '\n\n\n')
        return render(request, 'blog/create/post_create.html', {'post_form': post_form})

    def post(self, request):
        post_form = PostForm(request.POST)
        print('\n\n\n USER[POST]: \n', request.user, '\n\n\n')
        if post_form.is_valid():
            # post_form.save(commit=False)
            # post_form.author = request.user
            # print('\n\n\n AUTHOR:::\n', post_form.author, '\n\n\n')
            # post_form.save()
            post_form.save(commit=False)
            post_form.instance.author = request.user
            post_form.save()

            return render(request, 'blog/create/post_success_created.html')


# def comment_rating_change(request, comment_id):
#     comment = get_object_or_404(Comment, pk=comment_id)
#     if comment.comment_rating.get(request.POST('+')):
#         comment.comment_rating.rating -= 1
#     else:
#         comment.comment_rating.rating += 1
#

