from django import forms
from . models import Comment, Post, CommentRating


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class CommentRatingForm(forms.ModelForm):

    # rating_choice = forms.ModelChoiceField(widget=forms.RadioSelect(), empty_label=None)

    class Meta:
        model = CommentRating
        fields = ('rating',)


class SearchForm(forms.Form):
    query = forms.CharField()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'tags')