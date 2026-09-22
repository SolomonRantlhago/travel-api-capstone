from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from .views import (
    RegisterView,
    ProfileView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserListView,
    UserDetailView,
)


app_name = 'accounts'


urlpatterns = [
    path(
        'register/',
        RegisterView.as_view(),
        name='register'
    ),
    path(
        'login/',
        TokenObtainPairView.as_view(),
        name='login'
    ),
    path(
        'login/refresh/',
        TokenRefreshView.as_view(),
        name='login-refresh'
    ),
    path(
        'profile/',
        ProfileView.as_view(),
        name='profile'
    ),
    path(
        'password/change/',
        PasswordChangeView.as_view(),
        name='password-change'
    ),
    path(
        'password/reset/',
        PasswordResetRequestView.as_view(),
        name='password-reset'
    ),
    path(
        'password/reset/confirm/',
        PasswordResetConfirmView.as_view(),
        name='password-reset-confirm'
    ),
    path(
        'users/',
        UserListView.as_view(),
        name='user-list'
    ),
    path(
        'users/<int:pk>/',
        UserDetailView.as_view(),
        name='user-detail'
    ),
]