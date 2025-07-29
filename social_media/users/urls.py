from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentification
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Compte utilisateur
    path('account/', views.AccountView.as_view(), name='account'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
]
