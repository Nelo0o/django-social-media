from django.urls import path
from . import views
from users import views as user_views

app_name = 'follows'

urlpatterns = [
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('block/<str:username>/', user_views.block_follower, name='block_follower'),
    path('unblock/<str:username>/', user_views.unblock_follower, name='unblock_follower'),
]
