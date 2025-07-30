from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from .models import Tweet, Comment
from .forms import TweetForm, CommentForm


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    form_class = TweetForm
    template_name = 'tweets/create.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        messages.success(self.request, 'Tweet publié avec succès!')
        return super().form_valid(form)


@login_required
@require_POST
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    user_profile = request.user.profile
    
    existing_like = tweet.likes.filter(user=user_profile).first()
    
    if existing_like:
        existing_like.delete()
        liked = False
        message = 'Tweet retiré des favoris'
    else:
        tweet.likes.create(user=user_profile)
        liked = True
        message = 'Tweet ajouté aux favoris'
    
    # Si c'est une requête AJAX, retourner du JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': tweet.likes.count(),
            'message': message
        })
    
    # Sinon, redirection classique pour compatibilité
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


@login_required
@require_POST
def retweet_tweet(request, tweet_id):
    """Vue pour retweeter un tweet"""
    original_tweet = get_object_or_404(Tweet, id=tweet_id)
    user_profile = request.user.profile
    
    # Vérifier si l'utilisateur essaie de retweeter son propre tweet
    if original_tweet.author == user_profile:
        return JsonResponse({
            'success': False,
            'error': 'Vous ne pouvez pas retweeter votre propre tweet'
        }, status=400)
    
    # Vérifier si déjà retweeté
    existing_retweet = Tweet.objects.filter(
        author=user_profile,
        retweet_of=original_tweet
    ).first()
    
    if existing_retweet:
        return JsonResponse({
            'success': False,
            'retweeted': True,
            'retweet_count': original_tweet.retweet_count,
            'message': 'Vous avez déjà retweeté ce tweet'
        })
    
    # Créer le retweet
    retweet = Tweet.objects.create(
        author=user_profile,
        content='',  # Les retweets n'ont pas de contenu propre
        retweet_of=original_tweet
    )
    
    return JsonResponse({
        'success': True,
        'retweeted': True,
        'retweet_count': original_tweet.retweet_count,
        'message': 'Tweet retweeté avec succès'
    })


@login_required
@require_POST
def unretweet_tweet(request, tweet_id):
    """Vue pour annuler un retweet"""
    original_tweet = get_object_or_404(Tweet, id=tweet_id)
    user_profile = request.user.profile
    
    # Trouver et supprimer le retweet
    retweet = Tweet.objects.filter(
        author=user_profile,
        retweet_of=original_tweet
    ).first()
    
    if retweet:
        retweet.delete()
        retweeted = False
        message = 'Retweet annulé'
    else:
        retweeted = False
        message = 'Vous n\'aviez pas retweeté ce tweet'
    
    return JsonResponse({
        'success': True,
        'retweeted': retweeted,
        'retweet_count': original_tweet.retweet_count,
        'message': message
    })


def tweet_detail(request, tweet_id):
    """Affiche un tweet avec ses commentaires"""
    tweet = get_object_or_404(Tweet.objects.select_related(
        'author__user', 'retweet_of__author__user'
    ).prefetch_related(
        'likes', 'comments', 'retweets', 'hashtags',
        'retweet_of__likes', 'retweet_of__comments', 'retweet_of__retweets'
    ), id=tweet_id)
    
    comments = tweet.comments.select_related('author__user').order_by('created_at')
    
    # Ajouter les informations pour l'utilisateur connecté
    if request.user.is_authenticated:
        user_profile = request.user.profile
        original_tweet = tweet.original_tweet
        tweet.is_liked_by_user = original_tweet.likes.filter(user=user_profile).exists()
        tweet.is_retweeted_by_user = original_tweet.is_retweeted_by(user_profile)
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.tweet = tweet
            comment.author = request.user.profile
            comment.save()
            messages.success(request, 'Commentaire ajouté avec succès!')
            return redirect('tweets:detail', tweet_id=tweet.id)
    else:
        comment_form = CommentForm() if request.user.is_authenticated else None
    
    context = {
        'tweet': tweet,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'tweet_detail.html', context)


@login_required
@require_POST
def delete_tweet(request, tweet_id):
    """Supprimer un tweet (seulement par son auteur)"""
    tweet = get_object_or_404(Tweet, id=tweet_id)
    
    # Vérifier que l'utilisateur est bien l'auteur du tweet
    if tweet.author != request.user.profile:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Vous ne pouvez supprimer que vos propres tweets'
            }, status=403)
        else:
            messages.error(request, 'Vous ne pouvez supprimer que vos propres tweets')
            return redirect('core:home')
    
    # Supprimer le tweet
    tweet.delete()
    
    # Si c'est une requête AJAX, retourner du JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Tweet supprimé avec succès'
        })
    
    # Sinon rediriger avec un message
    messages.success(request, 'Tweet supprimé avec succès')
    return redirect('core:home')
