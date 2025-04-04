from . import views
from django.urls import path


app_name = "accounts"

urlpatterns = [
    path(
        '',
        views.LoginView.as_view(),
        name='login'
    ),
    path(
        'accounts/register/',
        views.RegisterView.as_view(),
        name='register'
    ),
    path(
        'accounts/logout/',
        views.LogoutView.as_view(),
        name="logout"
    ),
    path(
        'accounts/password-reset/',
        views.PasswordResetCustomView.as_view(),
        name="password_reset"
    ),
    path(
        'accounts/password-reset-confirm/<uidb64>/<token>',
        views.PasswordResetConfirmCustomView.as_view(),
        name="password_reset_confirm"
    ),
]
