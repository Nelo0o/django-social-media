from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline pour afficher le profil utilisateur dans l'admin User"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil utilisateur'
    fields = ('avatar', 'bio', 'city')


class UserAdmin(BaseUserAdmin):
    """Admin personnalisé pour User avec le profil intégré"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin pour les profils utilisateurs"""
    list_display = ('user', 'city', 'followers_count', 'following_count', 'date_joined')
    list_filter = ('city', 'date_joined')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'bio', 'city')
    readonly_fields = ('date_joined', 'followers_count', 'following_count')
    fields = ('user', 'avatar', 'bio', 'city', 'date_joined', 'followers_count', 'following_count')
    ordering = ('-date_joined',)
    
    def followers_count(self, obj):
        """Affiche le nombre d'abonnés"""
        return obj.followers_count
    followers_count.short_description = 'Abonnés'
    
    def following_count(self, obj):
        """Affiche le nombre d'abonnements"""
        return obj.following_count
    following_count.short_description = 'Abonnements'


# Désenregistrer l'admin User par défaut et enregistrer le nôtre
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
