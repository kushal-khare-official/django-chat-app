from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_online = models.BooleanField(default=True)
    groups = models.ManyToManyField('auth.Group', blank=True, related_name='custom_users')
    user_permissions = models.ManyToManyField('auth.Permission', blank=True, related_name='custom_users')

    def __str__(self):
        return self.username


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(CustomUser, related_name='chat_rooms')

    def __str__(self):
        return self.name


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='message')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.chat_room.name} - {self.timestamp}"
