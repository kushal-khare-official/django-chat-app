from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.user_registration, name='user_registration'),
    path('login/', views.user_login, name='user_login'),
    path('online-users/', views.get_online_users, name='get_online_users'),
    path('chat/start/', views.start_chat, name='start_chat'),
    path('suggested-friends/<int:user_id>/', views.suggested_friends, name='suggested_friends')
]
