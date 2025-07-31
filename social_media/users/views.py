from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .forms import InscriptionForm, UserProfileForm
from .models import UserProfile
from .services import UserService
from tweets.models import Tweet

class RegisterView(FormView):
    template_name = "register.html"
    form_class = InscriptionForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='users.backends.EmailBackend')
        messages.success(self.request, f'Bienvenue {user.username}!')
        return super().form_valid(form)

class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'account.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = kwargs.get('username')
        
        profile_data = UserService.get_user_profile_data(
            username=username,
            current_user=self.request.user
        )
        context.update(profile_data)
        
        user_tweets = UserService.get_user_tweets_with_metadata(
            profile=context['profile'],
            current_user=self.request.user
        )
        
        context['user_tweets'] = user_tweets
        context['tweets_count'] = user_tweets.count()
            
        return context

# Modifier le profil utilisateur connecté
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user.profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profil mis à jour!')
        return super().form_valid(form)

# Afficher le profil public d'un utilisateur
class PublicProfileView(TemplateView):
    template_name = 'public_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = kwargs.get('username')
        user = get_object_or_404(User, username=username)
        profile = user.profile
        
        context['profile_user'] = user
        context['profile'] = profile
        
        # Vérifier si l'utilisateur connecté suit ce profil
        if self.request.user.is_authenticated:
            context['is_following'] = self.request.user.profile.is_following(profile)
        else:
            context['is_following'] = False
            
        return context

# Rechercher des utilisateurs
class UserSearchView(TemplateView):
    template_name = 'user_search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        page = self.request.GET.get('page', 1)
        
        # Utiliser le service pour la recherche
        users = UserService.search_users(
            query=query,
            current_user=self.request.user,
            limit=100  # Limite plus élevée pour la pagination
        )
        
        # Pagination
        paginator = Paginator(users, 12)  # 12 utilisateurs par page
        page_obj = paginator.get_page(page)
        
        # Ajouter les informations de suivi pour l'utilisateur connecté
        if self.request.user.is_authenticated:
            for user_profile in page_obj:
                user_profile.is_followed_by_current_user = self.request.user.profile.is_following(user_profile)
        
        context.update({
            'query': query,
            'page_obj': page_obj,
            'users': page_obj,
            'total_results': paginator.count
        })
        
        return context

# Suggestions d'utilisateurs à suivre
@login_required
def user_suggestions(request):
    """API pour obtenir des suggestions d'utilisateurs à suivre"""
    # Utiliser le service pour obtenir les suggestions
    suggestions = UserService.get_user_suggestions(
        current_user=request.user,
        limit=5
    )
    
    suggestions_data = []
    for profile in suggestions:
        suggestions_data.append({
            'username': profile.user.username,
            'full_name': f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.username,
            'bio': profile.bio or '',
            'avatar_url': profile.avatar.url if profile.avatar else None,
            'followers_count': profile.followers_count,
            'profile_url': f'/profile/{profile.user.username}/'
        })
    
    return JsonResponse({
        'suggestions': suggestions_data
    })

# Supprimer le compte utilisateur
@login_required
def delete_account(request):
    """Vue pour supprimer le compte utilisateur"""
    if request.method == 'POST':
        user = request.user
        username = user.username
        
        # Déconnecter l'utilisateur
        logout(request)
        
        # Supprimer l'utilisateur
        user.delete()
        
        messages.success(request, f'Le compte {username} a été supprimé avec succès.')
        return redirect('core:home')
    
    return redirect('profile')

# Bloquer un follower
@login_required
def block_follower(request, username):
    """Bloquer un follower"""
    if request.method == 'POST':
        user_to_block = get_object_or_404(User, username=username)
        user_profile = user_to_block.profile
        
        # Vérifier que l'utilisateur nous suit avant de le bloquer
        if request.user.profile.follow_manager.block_follower(user_profile):
            return JsonResponse({
                'success': True,
                'message': f'{username} a été bloqué.',
                'blocked': True
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'{username} ne vous suit pas.',
                'blocked': False
            })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})

# Débloquer un follower
@login_required
def unblock_follower(request, username):
    """Débloquer un follower"""
    if request.method == 'POST':
        user_to_unblock = get_object_or_404(User, username=username)
        user_profile = user_to_unblock.profile
        
        if request.user.profile.follow_manager.unblock_follower(user_profile):
            return JsonResponse({
                'success': True,
                'message': f'{username} a été débloqué.',
                'blocked': False
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Impossible de débloquer {username}.',
                'blocked': True
            })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})

# Gérer les followers (avec options de blocage)
class ManageFollowersView(LoginRequiredMixin, TemplateView):
    template_name = 'manage_followers.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.profile
        
        # Récupérer tous les followers (bloqués et non bloqués)
        from follows.models import Follow
        all_follow_relations = Follow.objects.filter(
            followed=user_profile
        ).select_related('follower__user').order_by('-created_at')
        
        followers_data = []
        for follow_relation in all_follow_relations:
            follower_profile = follow_relation.follower
            followers_data.append({
                'profile': follower_profile,
                'user': follower_profile.user,
                'is_blocked': follow_relation.blocked,
                'follow_date': follow_relation.created_at
            })
        
        context['followers_data'] = followers_data
        context['total_followers'] = len(followers_data)
        context['blocked_count'] = sum(1 for f in followers_data if f['is_blocked'])
        context['active_count'] = sum(1 for f in followers_data if not f['is_blocked'])
        
        return context
