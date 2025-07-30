from django.db import models
import re


class Tweet(models.Model):
    author = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='tweets')
    content = models.TextField(max_length=280)
    image = models.ImageField(upload_to='tweets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    retweet_of = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='retweets')
    hashtags = models.ManyToManyField('Hashtag', blank=True, related_name='tweets')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.user.username}: {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        hashtags = re.findall(r'#(\w+)', self.content, re.IGNORECASE)
        self.hashtags.clear()
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(label=tag.lower())
            self.hashtags.add(hashtag)
    
    def get_content_without_hashtags(self):
        """Retourne le contenu sans les hashtags"""
        return re.sub(r'#\w+', '', self.content).strip()
    
    @property
    def is_retweet(self):
        """Vérifie si ce tweet est un retweet"""
        return self.retweet_of is not None
    
    @property
    def original_tweet(self):
        """Retourne le tweet original (pour les retweets)"""
        return self.retweet_of if self.is_retweet else self
    
    @property
    def retweet_count(self):
        """Nombre de retweets de ce tweet"""
        return self.retweets.count()
    
    def get_retweeters(self):
        """Retourne les profils qui ont retweeté ce tweet"""
        return [retweet.author for retweet in self.retweets.select_related('author__user')]
    
    def is_retweeted_by(self, user_profile):
        """Vérifie si un utilisateur a retweeté ce tweet"""
        return self.retweets.filter(author=user_profile).exists()


class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.user.username} commented"


class Like(models.Model):
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='likes')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'tweet')
    
    def __str__(self):
        return f"{self.user.user.username} liked tweet"


class Hashtag(models.Model):
    label = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"{self.label}"