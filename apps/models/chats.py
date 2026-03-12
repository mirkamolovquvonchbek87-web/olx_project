
from django.db.models import ForeignKey, CASCADE, SET_NULL, TextField, BooleanField ,FileField


from apps.models.base import CreatedBaseModel


class Chat(CreatedBaseModel):
    user1 = ForeignKey(
        "apps.User",
        CASCADE,
        related_name="chats_started"
    )

    user2 = ForeignKey(
        "apps.User",
        CASCADE,
        related_name="chats_received"
    )

    announcement = ForeignKey(
        "apps.Announcement",
        CASCADE,
        related_name="chats",
        null=True
    )

    def __str__(self):
        return f"{self.user1} - {self.user2}"

    @property
    def last_message(self):
        return self.messages.first()

    @staticmethod
    def get_or_create_chat(user1, user2):

        chat = Chat.objects.filter(
            user1=user1,
            user2=user2
        ).first()

        if chat:
            return chat, False

        chat = Chat.objects.filter(
            user1=user2,
            user2=user1
        ).first()

        if chat:
            return chat, False

        chat = Chat.objects.create(
            user1=user1,
            user2=user2
        )

        return chat, True






class Message(CreatedBaseModel):

    chat = ForeignKey(
        "apps.Chat",
        CASCADE,
        related_name="messages"
    )

    from_user = ForeignKey(
        "apps.User",
        SET_NULL,
        null=True,
        related_name="sent_messages"
    )
    message = TextField()

    is_read = BooleanField(default=False)

    def read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])

    file = FileField(
        upload_to="chat/files/",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.message[:30]

    class Meta:
        ordering = ["-created_at"]