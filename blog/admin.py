from django.contrib import admin
from . models import Post, Comment, Images, CommentRating
from django.utils.safestring import mark_safe


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


# @admin.register(CommentRating)
class CommentRatingInline(admin.TabularInline):
    # list_display = ('comment', 'rating')
    model = CommentRating
    fields = ('rating', )
    extra = 0


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'activate')
    list_filter = ('activate', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
    inlines = [
        CommentRatingInline,
    ]


@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('post', 'title', 'upload_time', 'get_image')

    def get_image(self, image):
        return mark_safe(f'<img src={image.image.url} width=50 height=55>')
