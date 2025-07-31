from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tweets.models import Tweet
from tweets.forms import TweetForm


class HomeView(TemplateView):
    """Vue principale pour la page d'accueil avec le feed"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les tweets récents avec les relations optimisées
        tweets = Tweet.objects.select_related(
            'author__user', 'retweet_of__author__user'
        ).prefetch_related(
            'likes', 'comments', 'retweets', 'hashtags',
            'retweet_of__likes', 'retweet_of__comments', 'retweet_of__retweets'
        ).order_by('-created_at')
        
        # Filtrer les tweets des utilisateurs bloqués si l'utilisateur est connecté
        if self.request.user.is_authenticated:
            from follows.models import Follow
            current_user_profile = self.request.user.profile
            
            # Exclure les tweets des utilisateurs qui ont bloqué l'utilisateur connecté
            blocked_by_users = Follow.objects.filter(
                follower=current_user_profile,
                blocked=True
            ).values_list('followed_id', flat=True)
            
            # Exclure les tweets des utilisateurs que l'utilisateur connecté a bloqués
            blocking_users = Follow.objects.filter(
                followed=current_user_profile,
                blocked=True
            ).values_list('follower_id', flat=True)
            
            # Combiner les deux listes d'exclusion
            excluded_users = list(blocked_by_users) + list(blocking_users)
            
            if excluded_users:
                tweets = tweets.exclude(author_id__in=excluded_users)
        
        tweets = tweets[:50]
        
        # Ajouter l'état du retweet pour l'utilisateur connecté
        if self.request.user.is_authenticated:
            user_profile = self.request.user.profile
            for tweet in tweets:
                original_tweet = tweet.original_tweet
                tweet.is_retweeted_by_user = original_tweet.is_retweeted_by(user_profile)
        
        context['tweets'] = tweets
        
        # Ajouter le formulaire de tweet pour les utilisateurs connectés
        if self.request.user.is_authenticated:
            context['tweet_form'] = TweetForm()
        
        return context
