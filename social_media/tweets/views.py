from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Tweet
from .forms import TweetForm


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
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    user_profile = request.user.profile
    
    existing_like = tweet.likes.filter(user=user_profile).first()
    
    if existing_like:
        existing_like.delete()
        liked = False
    else:
        tweet.likes.create(user=user_profile)
        liked = True
    
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))
