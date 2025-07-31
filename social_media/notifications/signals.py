from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from tweets.models import Like, Comment, Tweet
from follows.models import Follow
from .models import Notification


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """
    Crée une notification quand un utilisateur like un tweet
    """
    if created and instance.user != instance.tweet.author:
        # Ne pas créer de notification si l'utilisateur like son propre tweet
        Notification.objects.create(
            recipient=instance.tweet.author,
            sender=instance.user,
            tweet=instance.tweet,
            notification_type='like'
        )


@receiver(post_delete, sender=Like)
def delete_like_notification(sender, instance, **kwargs):
    """
    Supprime la notification quand un like est retiré
    """
    try:
        Notification.objects.filter(
            recipient=instance.tweet.author,
            sender=instance.user,
            tweet=instance.tweet,
            notification_type='like'
        ).delete()
    except (AttributeError, Tweet.DoesNotExist):
        pass


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """
    Crée une notification quand un utilisateur commente un tweet
    """
    if created and instance.author != instance.tweet.author:
        # Ne pas créer de notification si l'utilisateur commente son propre tweet
        Notification.objects.create(
            recipient=instance.tweet.author,
            sender=instance.author,
            tweet=instance.tweet,
            notification_type='comment'
        )


@receiver(post_delete, sender=Comment)
def delete_comment_notification(sender, instance, **kwargs):
    """
    Supprime la notification quand un commentaire est supprimé
    """
    try:
        Notification.objects.filter(
            recipient=instance.tweet.author,
            sender=instance.author,
            tweet=instance.tweet,
            notification_type='comment'
        ).delete()
    except (AttributeError, Tweet.DoesNotExist):
        pass


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """
    Crée une notification quand un utilisateur suit un autre utilisateur
    """
    if created and not instance.blocked:
        # Ne pas créer de notification si c'est bloqué
        Notification.objects.create(
            recipient=instance.followed,
            sender=instance.follower,
            notification_type='follow'
        )


@receiver(post_delete, sender=Follow)
def delete_follow_notification(sender, instance, **kwargs):
    """
    Supprime la notification quand un follow est supprimé
    """
    Notification.objects.filter(
        recipient=instance.followed,
        sender=instance.follower,
        notification_type='follow'
    ).delete()


@receiver(post_save, sender=Tweet)
def create_retweet_notification(sender, instance, created, **kwargs):
    """
    Crée une notification quand un utilisateur retweet un tweet
    """
    if created and instance.retweet_of and instance.author != instance.retweet_of.author:
        # C'est un retweet et ce n'est pas l'auteur original qui retweet son propre tweet
        Notification.objects.create(
            recipient=instance.retweet_of.author,
            sender=instance.author,
            tweet=instance.retweet_of,  # On référence le tweet original
            notification_type='retweet'
        )


@receiver(post_delete, sender=Tweet)
def delete_retweet_notification(sender, instance, **kwargs):
    """
    Supprime la notification quand un retweet est supprimé
    """
    try:
        if instance.retweet_of:
            Notification.objects.filter(
                recipient=instance.retweet_of.author,
                sender=instance.author,
                tweet=instance.retweet_of,
                notification_type='retweet'
            ).delete()
    except (AttributeError, Tweet.DoesNotExist):
        pass
