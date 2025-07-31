from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tweets.models import Tweet
from tweets.forms import TweetForm
from tweets.services import TweetService


class HomeView(TemplateView):
    """Vue principale pour la page d'accueil avec le feed"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Utiliser le service pour récupérer le fil d'actualité
        tweets = TweetService.get_home_feed(
            current_user=self.request.user,
            limit=50
        )
        
        # Ajouter les métadonnées d'interaction
        TweetService.add_user_interaction_metadata(tweets, self.request.user)
        
        context['tweets'] = tweets
        
        # Ajouter le formulaire de tweet pour les utilisateurs connectés
        if self.request.user.is_authenticated:
            context['tweet_form'] = TweetForm()
        
        return context
