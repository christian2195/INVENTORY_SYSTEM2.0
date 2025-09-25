# src/apps/users/views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserCreationForm, UserUpdateForm  # Debes crear estos formularios
from .models import User

class UserRegisterView(CreateView):
    """
    Vista para el registro de nuevos usuarios.
    """
    form_class = UserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

class UserProfileView(LoginRequiredMixin, DetailView):
    """
    Vista para ver el perfil del usuario actual.
    """
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para actualizar la información del perfil del usuario.
    """
    model = User
    form_class = UserUpdateForm
    template_name = 'users/update_profile.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('users:profile')

class UserRegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'users/register.html'
    success_url = '/login/'