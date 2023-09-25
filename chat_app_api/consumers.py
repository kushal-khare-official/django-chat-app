import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import CustomUser, ChatRoom, Message


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        self.room_name = ChatRoom.objects.get(id=room_id).name

        async_to_sync(self.channel_layer.group_add)(
            self.room_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name, self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        sender = CustomUser.objects.get(id=data['user_id'])
        message = data['message']
        room_id = self.scope['url_route']['kwargs']['chat_room_id']

        chat_room = ChatRoom.objects.get(id=room_id)

        if chat_room:
            message_obj = Message.objects.create(chat_room=chat_room, sender=sender, content=message)
            async_to_sync(self.channel_layer.group_send)(
                self.room_name,
                {"type": "chat_message",
                 "content": message_obj.content,
                 "sender": message_obj.sender.username,
                 "sender_id": message_obj.sender.id,
                 "timestamp": message_obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                 }
            )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'text': event['content'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
        }))
