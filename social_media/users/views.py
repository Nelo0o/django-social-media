from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.contrib import messages
from .forms import InscriptionForm, UserProfileForm
from .models import UserProfile


class InscriptionView(FormView):
    template_name = "register.html"
    form_class = InscriptionForm
    success_url = reverse_lazy('account')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Bienvenue {user.username}!')
        return super().form_valid(form)


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'account.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('account')
    
    def get_object(self):
        return self.request.user.profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profil mis à jour!')
        return super().form_valid(form)


class CustomLogoutView(LoginRequiredMixin, View):

    def get(self, request):
        return self.logout_user(request)
    
    def post(self, request):
        return self.logout_user(request)
    
    def logout_user(self, request):
        username = request.user.username
        logout(request)
        messages.success(request, f'Au revoir {username}!')
        return redirect('core:home')
