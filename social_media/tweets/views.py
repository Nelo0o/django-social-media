from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
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


def tweet_detail(request, tweet_id):
    """Affiche un tweet avec ses commentaires"""
    tweet = get_object_or_404(Tweet, id=tweet_id)
    comments = tweet.comments.select_related('author__user').order_by('created_at')
    
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
