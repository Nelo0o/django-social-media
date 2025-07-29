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
        context['page_title'] = 'Accueil'
        
        # Récupérer tous les tweets par ordre chronologique décroissant
        context['tweets'] = Tweet.objects.select_related(
            'author__user'
        ).prefetch_related(
            'likes__user__user',
            'comments__author__user'
        ).all()[:50]  # Limiter à 50 tweets pour la performance
        
        # Ajouter le formulaire de création de tweet si l'utilisateur est connecté
        if self.request.user.is_authenticated:
            context['tweet_form'] = TweetForm()
        
        return context
