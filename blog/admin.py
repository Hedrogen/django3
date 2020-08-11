from django.contrib import admin
from . models import Post, Comment, Images, CommentRating
from django.utils.safestring import mark_safe
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from blog.models import Post


class PostAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = '__all__'


@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('post', 'title', 'upload_time', 'get_image')

    def get_image(self, image):
        return mark_safe(f'<img src={image.image.url} width=50 height=55>')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    form = PostAdminForm
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


class CommentRatingInline(admin.TabularInline):
    model = CommentRating
    fields = ('rating', )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'activate')
    list_filter = ('activate', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
    inlines = [
        CommentRatingInline,
    ]



