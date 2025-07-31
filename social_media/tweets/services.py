from django.db.models import Q
from .models import Tweet


class TweetService:
    @staticmethod
    def get_home_feed(current_user=None, limit=50):
        tweets = Tweet.objects.with_interactions().with_counts().order_by('-created_at')
        
        if current_user and current_user.is_authenticated:
            tweets = TweetService._filter_blocked_users(tweets, current_user)
        
        return tweets[:limit]
    
    @staticmethod
    def _filter_blocked_users(tweets_queryset, current_user):
        from follows.models import Follow
        
        profile = current_user.profile
        blocked_users = Follow.objects.filter(
            Q(follower=profile, blocked=True) | Q(followed=profile, blocked=True)
        ).values_list('followed_id', 'follower_id')
        
        excluded_ids = set()
        for followed_id, follower_id in blocked_users:
            excluded_ids.update([followed_id, follower_id])
        
        return tweets_queryset.exclude(author_id__in=excluded_ids) if excluded_ids else tweets_queryset
    
    @staticmethod
    def add_user_interaction_metadata(tweets, current_user):
        if not current_user or not current_user.is_authenticated:
            return
        
        user_profile = current_user.profile
        for tweet in tweets:
            original_tweet = tweet.original_tweet
            tweet.user_has_liked = original_tweet.likes.filter(user=user_profile).exists()
            tweet.user_has_retweeted = original_tweet.is_retweeted_by(user_profile)
            tweet.is_liked_by_user = tweet.user_has_liked
            tweet.is_retweeted_by_user = tweet.user_has_retweeted
    
    @staticmethod
    def get_tweets_by_hashtag(hashtag_label, current_user=None, limit=1000):
        user_profile = current_user.profile if current_user and current_user.is_authenticated else None
        return Tweet.objects.by_hashtag(hashtag_label, user_profile)[:limit]
    
    @staticmethod
    def get_tweet_with_comments(tweet_id, current_user=None):
        try:
            tweet = Tweet.objects.with_interactions().with_counts().get(id=tweet_id)
            comments = tweet.comments.select_related('author__user').order_by('-created_at')
            
            if current_user and current_user.is_authenticated:
                TweetService.add_user_interaction_metadata([tweet], current_user)
            
            return tweet, comments
        except Tweet.DoesNotExist:
            return None, None
