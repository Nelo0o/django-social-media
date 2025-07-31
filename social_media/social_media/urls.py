"""
URL configuration for social_media project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    
    # URLs d'authentification courtes
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', user_views.RegisterView.as_view(), name='register'),
    
    # URLs de profil courtes
    path('profile/', user_views.AccountView.as_view(), name='profile'),
    path('profile/edit/', user_views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/delete/', user_views.delete_account, name='delete_account'),
    path('profile/followers/', user_views.ManageFollowersView.as_view(), name='manage_followers'),
    path('profile/<str:username>/', user_views.AccountView.as_view(), name='public_profile'),
    
    # URLs de follow/unfollow
    path('', include('follows.urls')),
    
    # URLs de recherche d'utilisateurs
    path('search/', user_views.UserSearchView.as_view(), name='user_search'),
    path('api/suggestions/', user_views.user_suggestions, name='user_suggestions'),
    
    # URLs des tweets
    path('tweets/', include('tweets.urls')),
    
    # URLs des notifications
    path('notifications/', include('notifications.urls')),
    
    # Garder users/ pour d'autres fonctionnalités futures
    path('users/', include('users.urls')),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)