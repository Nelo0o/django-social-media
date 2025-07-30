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
        ).order_by('-created_at')[:50]
        
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
