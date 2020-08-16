from django import forms
from . models import Comment, Post, CommentRating
from ckeditor.widgets import CKEditorWidget


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        widgets = {'user': forms.HiddenInput()}
        fields = ('body', 'user')


class CommentRatingForm(forms.ModelForm):

    post_rating = forms.IntegerField()

    class Meta:
        model = CommentRating
        fields = ('rating',)


class SearchForm(forms.Form):
    query = forms.CharField()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        widgets = {'author': forms.HiddenInput()}
        fields = ['title', 'body', 'tags', 'author']
