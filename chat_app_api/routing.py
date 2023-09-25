from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('api/chat/send/<int:chat_room_id>', consumers.ChatConsumer.as_asgi())
]
