from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from .models import Tweet, Comment, Hashtag
from .forms import TweetForm, CommentForm
from .services import TweetService


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
    original_tweet = tweet.original_tweet
    user_profile = request.user.profile
    
    existing_like = original_tweet.likes.filter(user=user_profile).first()
    
    if existing_like:
        existing_like.delete()
        liked, message = False, 'Tweet retiré des favoris'
    else:
        original_tweet.likes.create(user=user_profile)
        liked, message = True, 'Tweet ajouté aux favoris'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': original_tweet.likes.count(),
            'original_tweet_id': original_tweet.id,
            'message': message
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


@login_required
@require_POST
def retweet_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    original_tweet = tweet.original_tweet
    user_profile = request.user.profile
    
    existing_retweet = Tweet.objects.filter(
        author=user_profile,
        retweet_of=original_tweet
    ).first()
    
    if existing_retweet:
        existing_retweet.delete()
        retweeted, message = False, 'Retweet annulé'
    else:
        Tweet.objects.create(
            author=user_profile,
            content='',
            retweet_of=original_tweet
        )
        retweeted, message = True, 'Tweet retweeté avec succès'
    
    return JsonResponse({
        'success': True,
        'retweeted': retweeted,
        'retweets_count': original_tweet.retweet_count,
        'original_tweet_id': original_tweet.id,
        'message': message
    })


def tweet_detail(request, tweet_id):
    """Affiche un tweet avec ses commentaires"""
    # Utiliser le service pour récupérer le tweet et ses commentaires
    tweet, comments = TweetService.get_tweet_with_comments(
        tweet_id=tweet_id,
        current_user=request.user
    )
    
    if not tweet:
        # Tweet non trouvé
        from django.http import Http404
        raise Http404("Tweet non trouvé")
    
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


class HashtagTweetsView(ListView):
    """Vue pour afficher tous les tweets contenant un hashtag spécifique"""
    model = Tweet
    template_name = 'hashtag_tweets.html'
    context_object_name = 'tweets'
    paginate_by = 20
    
    def get_queryset(self):
        self.hashtag = get_object_or_404(Hashtag, label=self.kwargs['hashtag_label'])
        
        # Utiliser le service pour récupérer les tweets du hashtag
        tweets = TweetService.get_tweets_by_hashtag(
            hashtag_label=self.hashtag.label,
            current_user=self.request.user,
            limit=1000  # Limite élevée pour la pagination
        )
        
        # Ajouter les métadonnées d'interaction
        TweetService.add_user_interaction_metadata(tweets, self.request.user)
        
        return tweets
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hashtag'] = self.hashtag
        context['tweets_count'] = self.get_queryset().count()
        return context


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
