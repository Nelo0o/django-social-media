from django.db import models


class Follow(models.Model):
    follower = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='followers')
    blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'followed')
    
    def __str__(self):
        return f"{self.follower.user.username} follows {self.followed.user.username}"