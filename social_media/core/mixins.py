from django.contrib.auth.mixins import LoginRequiredMixin
from tweets.services import TweetService


class TweetInteractionMixin:
    """
    Mixin pour ajouter les métadonnées d'interaction aux tweets
    """
    
    def add_tweet_metadata(self, tweets):
        """
        Ajoute les métadonnées d'interaction (likes, retweets) aux tweets
        
        Args:
            tweets: Liste ou QuerySet de tweets
        """
        if hasattr(self.request, 'user'):
            TweetService.add_user_interaction_metadata(tweets, self.request.user)


class BlockedUserFilterMixin:
    """
    Mixin pour filtrer les utilisateurs bloqués dans les requêtes
    """
    
    def filter_blocked_users(self, queryset, user_field='author'):
        """
        Filtre les objets liés aux utilisateurs bloqués
        
        Args:
            queryset: QuerySet à filtrer
            user_field: Nom du champ utilisateur à filtrer
            
        Returns:
            QuerySet: QuerySet filtré
        """
        if not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
            return queryset
        
        from follows.models import Follow
        
        current_user_profile = self.request.user.profile
        
        # Obtenir les utilisateurs bloqués (bidirectionnel)
        blocked_by_users = Follow.objects.filter(
            follower=current_user_profile,
            blocked=True
        ).values_list('followed_id', flat=True)
        
        blocking_users = Follow.objects.filter(
            followed=current_user_profile,
            blocked=True
        ).values_list('follower_id', flat=True)
        
        excluded_users = list(blocked_by_users) + list(blocking_users)
        
        if excluded_users:
            filter_kwargs = {f'{user_field}_id__in': excluded_users}
            queryset = queryset.exclude(**filter_kwargs)
        
        return queryset


class UserContextMixin:
    """
    Mixin pour ajouter des informations utilisateur au contexte
    """
    
    def get_user_context_data(self, **kwargs):
        """
        Ajoute les informations utilisateur au contexte
        
        Returns:
            dict: Données de contexte utilisateur
        """
        context = {}
        
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            context['current_user_profile'] = self.request.user.profile
            
            # Ajouter le nombre de notifications non lues
            from notifications.models import Notification
            context['unread_notifications_count'] = Notification.get_unread_count(
                self.request.user.profile
            )
        
        return context


class PaginationMixin:
    """
    Mixin pour standardiser la pagination
    """
    paginate_by = 20
    
    def get_paginate_by(self, queryset):
        """
        Permet de personnaliser le nombre d'éléments par page
        """
        return self.request.GET.get('per_page', self.paginate_by)


class OptimizedQueryMixin:
    """
    Mixin pour optimiser les requêtes avec select_related et prefetch_related
    """
    
    def get_optimized_queryset(self, queryset, select_fields=None, prefetch_fields=None):
        """
        Optimise un QuerySet avec select_related et prefetch_related
        
        Args:
            queryset: QuerySet à optimiser
            select_fields: Liste des champs pour select_related
            prefetch_fields: Liste des champs pour prefetch_related
            
        Returns:
            QuerySet: QuerySet optimisé
        """
        if select_fields:
            queryset = queryset.select_related(*select_fields)
        
        if prefetch_fields:
            queryset = queryset.prefetch_related(*prefetch_fields)
        
        return queryset
