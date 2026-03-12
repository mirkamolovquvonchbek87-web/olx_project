
import json
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
        message = data["message"]

        msg = await self.save_message(message)

        await self.channel_layer.group_send(
            self.room,
            {
                "type": "chat_message",
                "message": msg.message
            }
        )

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)

        message = data.get("message")
        file = data.get("file")
        filename = data.get("filename")

        msg = await self.save_message(message)

        await self.send(text_data=json.dumps({
            "message": message,
            "file": file,
            "filename": filename
        }))

    @sync_to_async
    def save_message(self, text):
        return Message.objects.create(
            chat_id=self.chat_id,
            message=text
        )