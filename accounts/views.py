from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.generic import View, DetailView, ListView, FormView, CreateView
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from django.contrib import messages


class UserLogin(View):

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


class UserRegistration(View):

    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request, 'account/registration.html', {'user_form': user_form})

    def post(self, request):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, 'account/registration_done.html', {'user_form': user_form})


class EditProfile(View):

    def get(self, request):
        user_form = UserEditForm(instance=request.user)
        # profile_form = ProfileEditForm(instance=request.user.profile)
        profile_form = ProfileEditForm(instance=request.user.profile)

        return render(request, 'account/user_account.html', {'user_form': user_form,
                                                             'profile_form': profile_form})

    def post(self, request):
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


@login_required
def user_account(request):
    return render(request, 'account/user_account.html', {'section': 'user_account'})

