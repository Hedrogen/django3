from django.db.models.signals import post_save
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.generic import View, DetailView, ListView, FormView, CreateView
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from django.contrib import messages
from django.dispatch import receiver
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from blog.models import Post


import logging


logger = logging.getLogger('accounts_views')


class UserLogin(View):

    """ Авторизация пользователя """

    def get(self, request):
        form = LoginForm()
        return render(request, 'account/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Activate')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
        return render(request, 'account/login.html', {'form': form})


class UserProfile(ListView):

    template_name = 'account/user_profile.html'
    # context_object_name = ''

    def get_queryset(self):
        """ Если не определить, то ничего не работает"""
        pass

    def get_context_data(self, *args, **kwargs):
        context = super(UserProfile, self).get_context_data(*args, **kwargs)
        # context = super(ListView, self).get_context_data(self.kwargs)
        if self.kwargs.get('username') is not None:
            user_profile = get_object_or_404(User, username=self.kwargs.get('username'))
            user_posts = user_profile.blog_posts.all()
            # tags = user_posts.tags.all()
            context['user_profile'] = user_profile
            context['posts'] = user_posts
            # context['tags'] = tags
        return context


class UserRegistration(View):

    """ Регистрация пользователя"""

    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request, 'account/registration.html', {'user_form': user_form})

    def post(self, request):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            cd = user_form.cleaned_data
            email_used = User.objects.filter(email=cd['email']).count()
            if email_used == 0:
                new_user = user_form.save(commit=False)
                new_user.set_password(user_form.cleaned_data['password'])
                new_user.save()
                messages.success(request, 'Account successfully registered')
                return render(request, 'account/registration_done.html', {'user_form': user_form})
            else:
                messages.error(request, 'Email already using')
                return render(request, 'account/registration.html')
        else:
            messages.error(request, 'Username must be unique')
            return render(request, 'account/registration.html')


class EditProfile(View):

    """ Изменение профиля пользователя """

    def get(self, request):
        try:
            user_form = UserEditForm(instance=request.user)
            profile_form = ProfileEditForm(instance=request.user.profile)

            return render(request, 'account/user_account.html', {'user_form': user_form,
                                                                 'profile_form': profile_form})
        except AttributeError:
            return render(request, 'account/user_account_error.html', status=404)

    def post(self, request):
        try:
            user_form = UserEditForm(
                instance=request.user,
                data=request.POST)
            profile_form = ProfileEditForm(
                instance=request.user.profile,
                data=request.POST,
                files=request.FILES)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Profile updated')
            else:
                messages.error(request, 'Error updating profile')
            return render(request, 'account/user_account.html', {'user_form': user_form,
                                                                 'profile_form': profile_form})
        except AttributeError:
            return render(request, 'account/user_account_error.html', status=404)


@login_required
def user_account(request):
    return render(request, 'account/user_account.html', {'section': 'user_account'})


@receiver(post_save, sender=User)
def save_or_create_profile(sender, instance, created, **kwargs):

    """ Функция отвечвет за создаине профиля """

    if created:
        Profile.objects.create(user=instance)
    else:
        try:
            instance.profile.save()
        except ObjectsDoesNotExist:
            Profile.objects.create(user=instance)
