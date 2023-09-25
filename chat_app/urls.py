from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('chat/<int:room_id>', views.chat_view, name='chat'),
    path('register/', views.user_registration, name='user_registration'),
    path('login/', views.user_login, name='user_login'),
]
