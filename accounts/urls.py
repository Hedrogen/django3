from django.urls import path
from . views import UserLogin, user_account, UserRegistration, EditProfile
from django.contrib.auth.views import *
from django.urls import reverse_lazy

app_name = 'accounts'

urlpatterns = [
    path('', EditProfile.as_view(), name='account'),  # требуется серьезная доработка

    path('login/', LoginView.as_view(
        template_name='account/login.html'), name='login'),
    path('logout/', LogoutView.as_view(
        template_name='account/logout.html'), name='logout'),
    path('registration/', UserRegistration.as_view(), name='registration'),

    path('password/change/', PasswordChangeView.as_view(
        template_name='account/pass_change.html',
        success_url=reverse_lazy('accounts:password_change_done')),
        name='pass_change'),
    path('password/change/done', PasswordChangeDoneView.as_view(
        template_name='account/pass_done.html'), name='password_change_done'),
    path('password_reset/', PasswordResetView.as_view(success_url=reverse_lazy('accounts:password_reset_done')), name='password_reset'),
    path('password_reset/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(success_url=reverse_lazy('accounts:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]