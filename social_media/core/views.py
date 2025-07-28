from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Vue principale pour la page d'accueil avec le feed"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Accueil'
        return context
