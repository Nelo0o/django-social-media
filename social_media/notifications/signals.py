from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from tweets.models import Like, Comment, Tweet
from follows.models import Follow
from .models import Notification
from .services import NotificationService


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """
    Crée une notification quand un utilisateur like un tweet
    """
    if created:
        NotificationService.create_notification(
            notification_type='like',
            sender_profile=instance.user,
            recipient_profile=instance.tweet.author,
            tweet=instance.tweet
        )


@receiver(post_delete, sender=Like)
def delete_like_notification(sender, instance, **kwargs):
    """
    Supprime la notification quand un like est retiré
    """
    NotificationService.delete_notification(
        notification_type='like',
        sender_profile=instance.user,
        recipient_profile=instance.tweet.author,
        tweet=instance.tweet
    )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """
    Crée une notification quand un utilisateur commente un tweet
    """
    if created:
        NotificationService.create_notification(
            notification_type='comment',
            sender_profile=instance.author,
            recipient_profile=instance.tweet.author,
            tweet=instance.tweet
        )


@receiver(post_delete, sender=Comment)
def delete_comment_notification(sender, instance, **kwargs):
    """
    Supprime la notification quand un commentaire est supprimé
    """
    NotificationService.delete_notification(
        notification_type='comment',
        sender_profile=instance.author,
        recipient_profile=instance.tweet.author,
        tweet=instance.tweet
    )


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """
    Crée une notification quand un utilisateur suit un autre utilisateur
    """
    if created and not instance.blocked:
        NotificationService.create_notification(
            notification_type='follow',
            sender_profile=instance.follower,
            recipient_profile=instance.followed
        )


@receiver(post_delete, sender=Follow)
def delete_follow_notification(sender, instance, **kwargs):
    """
    Supprime la notification quand un follow est supprimé
    """
    NotificationService.delete_notification(
        notification_type='follow',
        sender_profile=instance.follower,
        recipient_profile=instance.followed
    )


@receiver(post_save, sender=Tweet)
def create_retweet_notification(sender, instance, created, **kwargs):
    """
    Crée une notification quand un utilisateur retweet un tweet
    """
    if created and instance.retweet_of:
        NotificationService.create_notification(
            notification_type='retweet',
            sender_profile=instance.author,
            recipient_profile=instance.retweet_of.author,
            tweet=instance.retweet_of
        )


@receiver(post_delete, sender=Tweet)
def delete_retweet_notification(sender, instance, **kwargs):
    """
    Supprime la notification quand un retweet est supprimé
    """
    if instance.retweet_of:
        NotificationService.delete_notification(
            notification_type='retweet',
            sender_profile=instance.author,
            recipient_profile=instance.retweet_of.author,
            tweet=instance.retweet_of
        )
