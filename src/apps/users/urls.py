# src/apps/users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    UserRegisterView,
    UserProfileView,
    UserUpdateView,
)

app_name = 'users'

urlpatterns = [
    # URLs de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # URLs de gestión de usuarios
    path('registro/', UserRegisterView.as_view(), name='register'),
    path('perfil/', UserProfileView.as_view(), name='profile'),
    path('perfil/editar/', UserUpdateView.as_view(), name='update_profile'),
]