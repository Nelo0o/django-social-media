from django.urls import path
from . import views

app_name = 'tweets'

urlpatterns = [
    path('create/', views.TweetCreateView.as_view(), name='create'),
    path('<int:tweet_id>/like/', views.like_tweet, name='like'),
]
