"""
Template tags personnalisés pour simplifier les templates
"""
from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('partials/user_avatar.html')
def user_avatar(user_profile, size='medium', border=False):
    """
    Affiche l'avatar d'un utilisateur avec différentes tailles
    Usage: {% user_avatar user.profile size='large' border=True %}
    """
    return {
        'user_profile': user_profile,
        'size': size,
        'border': border
    }

@register.inclusion_tag('partials/follow_button.html', takes_context=True)
def follow_button(context, target_user, is_following=False):
    """
    Affiche le bouton follow/unfollow
    Usage: {% follow_button target_user is_following %}
    """
    user = context['user']
    return {
        'user': user,
        'target_username': target_user.username,
        'is_following': is_following,
        'is_own_profile': user == target_user if user.is_authenticated else False
    }

@register.inclusion_tag('partials/tweet_actions.html', takes_context=True)
def tweet_actions(context, tweet):
    """
    Affiche les actions d'un tweet (like, retweet, commentaire)
    Usage: {% tweet_actions tweet %}
    """
    return {
        'user': context['user'],
        'tweet': tweet
    }

@register.inclusion_tag('partials/user_stats.html')
def user_stats(stats):
    """
    Affiche les statistiques d'un utilisateur
    Usage: {% user_stats user_stats %}
    """
    return {
        'stats': stats
    }

@register.inclusion_tag('partials/tweet_composer.html', takes_context=True)
def tweet_composer(context, tweet_form):
    """
    Affiche le compositeur de tweet
    Usage: {% tweet_composer tweet_form %}
    """
    return {
        'user': context['user'],
        'tweet_form': tweet_form
    }

@register.filter
def user_display_name(user):
    """
    Retourne le nom d'affichage de l'utilisateur
    Usage: {{ user|user_display_name }}
    """
    if user.first_name or user.last_name:
        return f"{user.first_name} {user.last_name}".strip()
    return user.username

@register.filter
def format_count(value):
    """
    Formate les nombres pour l'affichage (1.2K, 1.5M, etc.)
    Usage: {{ count|format_count }}
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return 0
    
    if value >= 1000000:
        return f"{value/1000000:.1f}M"
    elif value >= 1000:
        return f"{value/1000:.1f}K"
    return str(value)

@register.simple_tag
def is_following(current_user, target_user):
    """
    Vérifie si l'utilisateur actuel suit l'utilisateur cible
    Usage: {% is_following user target_user as following %}
    """
    if not current_user.is_authenticated:
        return False
    
    from follows.models import Follow
    return Follow.objects.filter(
        follower=current_user.profile,
        followed=target_user.profile,
        blocked=False
    ).exists()

@register.simple_tag
def tweet_url(tweet):
    """
    Génère l'URL d'un tweet
    Usage: {% tweet_url tweet %}
    """
    return reverse('tweets:detail', kwargs={'tweet_id': tweet.id})

@register.filter
def add_css_class(field, css_class):
    """
    Ajoute une classe CSS à un champ de formulaire
    Usage: {{ form.field|add_css_class:"ma-classe" }}
    """
    return field.as_widget(attrs={'class': css_class})

@register.simple_tag(takes_context=True)
def active_page(context, url_name):
    """
    Retourne 'active' si la page actuelle correspond à l'URL
    Usage: {% active_page 'home' %}
    """
    request = context['request']
    if request.resolver_match and request.resolver_match.url_name == url_name:
        return 'active'
    return ''

@register.filter
def hashtag_links(content):
    """
    Convertit les hashtags en liens cliquables
    Usage: {{ tweet.content|hashtag_links }}
    """
    import re
    from django.urls import reverse
    
    def replace_hashtag(match):
        hashtag = match.group(1)
        url = reverse('tweets:hashtag', kwargs={'hashtag_label': hashtag})
        return f'<a href="{url}" class="text-x-blue hover:text-x-purple hover:underline transition-colors">#{hashtag}</a>'
    
    # Regex pour détecter les hashtags
    pattern = r'#(\w+)'
    result = re.sub(pattern, replace_hashtag, content)
    return mark_safe(result)

@register.filter
def mention_links(content):
    """
    Convertit les mentions en liens cliquables
    Usage: {{ tweet.content|mention_links }}
    """
    import re
    from django.urls import reverse
    
    def replace_mention(match):
        username = match.group(1)
        url = reverse('public_profile', kwargs={'username': username})
        return f'<a href="{url}" class="text-x-blue hover:text-x-purple hover:underline transition-colors">@{username}</a>'
    
    # Regex pour détecter les mentions
    pattern = r'@(\w+)'
    result = re.sub(pattern, replace_mention, content)
    return mark_safe(result)
