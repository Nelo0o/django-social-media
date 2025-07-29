from django.db import models


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