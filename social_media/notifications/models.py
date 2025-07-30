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
    
    def get_message(self):
        """Retourne un message formaté pour la notification"""
        if self.notification_type == 'like':
            return f"{self.sender.user.username} a aimé votre tweet"
        elif self.notification_type == 'comment':
            return f"{self.sender.user.username} a commenté votre tweet"
        elif self.notification_type == 'follow':
            return f"{self.sender.user.username} vous suit maintenant"
        elif self.notification_type == 'retweet':
            return f"{self.sender.user.username} a retweeté votre tweet"
        return "Nouvelle notification"
    
    def mark_as_seen(self):
        """Marque la notification comme vue"""
        self.seen = True
        self.save()
    
    @classmethod
    def get_unread_count(cls, user_profile):
        """Retourne le nombre de notifications non lues pour un utilisateur"""
        return cls.objects.filter(recipient=user_profile, seen=False).count()
    
    @classmethod
    def mark_all_as_seen(cls, user_profile):
        """Marque toutes les notifications comme vues pour un utilisateur"""
        cls.objects.filter(recipient=user_profile, seen=False).update(seen=True)
