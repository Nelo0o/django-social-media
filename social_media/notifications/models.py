from django.db import models


NOTIFICATION_TYPES = (
    ('like', 'Like'),
    ('retweet', 'Retweet'),
    ('follow', 'Follow'),
    ('comment', 'Comment'),
)


class Notification(models.Model):
    recipient = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='sent_notifications')
    tweet = models.ForeignKey('tweets.Tweet', on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.user.username}"
