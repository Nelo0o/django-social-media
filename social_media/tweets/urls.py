from django.urls import path
from . import views

app_name = 'tweets'

urlpatterns = [
    path('create/', views.TweetCreateView.as_view(), name='create'),
    path('<int:tweet_id>/', views.tweet_detail, name='detail'),
    path('<int:tweet_id>/like/', views.like_tweet, name='like'),
    path('<int:tweet_id>/retweet/', views.retweet_tweet, name='retweet'),
    path('<int:tweet_id>/unretweet/', views.unretweet_tweet, name='unretweet'),
    path('<int:tweet_id>/delete/', views.delete_tweet, name='delete'),
    path('hashtag/<str:hashtag_label>/', views.HashtagTweetsView.as_view(), name='hashtag'),
]
