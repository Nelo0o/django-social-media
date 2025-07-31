from django.db import models
from django.db.models import Count, Q


class UserProfileQuerySet(models.QuerySet):
    """QuerySet personnalisé pour optimiser les requêtes de profils utilisateurs"""
    
    def with_user_data(self):
        """
        Précharge les données utilisateur
        """
        return self.select_related('user')
    
    def with_stats(self):
        """
        Ajoute les statistiques via annotations
        """
        return self.annotate(
            tweets_count_db=Count('tweets', distinct=True),
            followers_count_db=Count('followers', distinct=True),
            following_count_db=Count('following', distinct=True),
            likes_count_db=Count('likes', distinct=True),
            comments_count_db=Count('comments', distinct=True)
        )
    
    def exclude_blocked_users(self, current_user_profile):
        """
        Exclut les utilisateurs bloqués (bidirectionnel)
        """
        if not current_user_profile:
            return self
        
        from follows.models import Follow
        
        # Utilisateurs qui ont bloqué l'utilisateur connecté
        blocked_by_users = Follow.objects.filter(
            follower=current_user_profile,
            blocked=True
        ).values_list('followed_id', flat=True)
        
        # Utilisateurs que l'utilisateur connecté a bloqués
        blocking_users = Follow.objects.filter(
            followed=current_user_profile,
            blocked=True
        ).values_list('follower_id', flat=True)
        
        excluded_users = list(blocked_by_users) + list(blocking_users)
        
        if excluded_users:
            return self.exclude(id__in=excluded_users)
        
        return self
    
    def search_by_query(self, query):
        """
        Recherche par nom, prénom, username ou ville
        """
        if not query or len(query.strip()) < 2:
            return self.none()
        
        return self.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(city__icontains=query)
        ).distinct()
    
    def popular(self):
        """
        Trie par popularité (nombre de followers)
        """
        return self.with_stats().order_by('-followers_count_db', 'user__username')
    
    def for_suggestions(self, current_user_profile, limit=5):
        """
        QuerySet optimisé pour les suggestions d'utilisateurs
        """
        if not current_user_profile:
            return self.none()
        
        # Utilisateurs déjà suivis
        following_ids = current_user_profile.following.values_list('id', flat=True)
        
        return self.with_user_data().with_stats().exclude(
            id__in=list(following_ids) + [current_user_profile.id]
        ).exclude_blocked_users(current_user_profile).filter(
            followers_count_db__gt=0  # Au moins un follower
        ).order_by('-followers_count_db', '-tweets_count_db')[:limit]
    
    def for_search(self, query, current_user_profile=None, limit=100):
        """
        QuerySet optimisé pour la recherche d'utilisateurs
        """
        queryset = self.with_user_data().search_by_query(query)
        
        if current_user_profile:
            queryset = queryset.exclude(user=current_user_profile.user)
            queryset = queryset.exclude_blocked_users(current_user_profile)
        
        return queryset.popular()[:limit]


class UserProfileManager(models.Manager):
    """Manager personnalisé pour le modèle UserProfile"""
    
    def get_queryset(self):
        return UserProfileQuerySet(self.model, using=self._db)
    
    def with_user_data(self):
        return self.get_queryset().with_user_data()
    
    def with_stats(self):
        return self.get_queryset().with_stats()
    
    def for_suggestions(self, current_user_profile, limit=5):
        return self.get_queryset().for_suggestions(current_user_profile, limit)
    
    def for_search(self, query, current_user_profile=None, limit=100):
        return self.get_queryset().for_search(query, current_user_profile, limit)
