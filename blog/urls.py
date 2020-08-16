from .feeds import LatestPostsFeed
from django.urls import path
from . import views


app_name = 'blog'


urlpatterns = [
    path('', views.post_list, name='post_list'),
    # path('comment/rating/change/<int:pk>', views.comment_rating_change(), name='comment_rating_change_url'),
    path('post/create/', views.PostCreate.as_view(), name='post_create_url'),

    path('post/edit/<slug:slug>', views.PostEdit.as_view(), name='post_edit_url'),

    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),

    path('<int:year>/<int:month>/<int:day>/<slug:post>', views.post_detail, name='post_detail'),

    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('feed/', LatestPostsFeed(), name='post_feed'),

    path('search/', views.post_search, name='post_search'),
]
