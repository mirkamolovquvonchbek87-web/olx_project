import json
import base64
from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from apps.models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room = f"chat_{self.chat_id}"

        await self.channel_layer.group_add(
            self.room,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        file_data = data.get("file")
        filename = data.get("filename")

        user = self.scope.get("user")
        user_id = user.id if user and user.is_authenticated else None

        msg = await self.save_message(user_id, message, file_data, filename)

        await self.channel_layer.group_send(
            self.room,
            {
                "type": "chat_message",
                "message": msg.message,
                "user_id": user_id,
                "file_url": msg.file.url if msg.file else None,
                "created_at": msg.created_at.strftime("%H:%M")
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "user_id": event.get("user_id"),
            "file_url": event.get("file_url"),
            "created_at": event.get("created_at"),
        }))

    @sync_to_async
    def save_message(self, user_id, text, file_data, filename):
        msg = Message(
            chat_id=self.chat_id,
            from_user_id=user_id,
            message=text
        )
        if file_data and filename:
            try:
                format, imgstr = file_data.split(';base64,')
                ext = filename.split('.')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=filename)
                msg.file = data
            except Exception as e:
                pass
                
        msg.save()
        return msg