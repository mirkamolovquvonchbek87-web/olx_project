from django.db.models import CharField, CASCADE, ForeignKey, JSONField, TextChoices
from django.db.models.fields import PositiveIntegerField, PositiveSmallIntegerField, TextField
from apps.models.base import ImageBaseModel, SlugBaseModel, CreatedBaseModel




class Announcement(SlugBaseModel, CreatedBaseModel):
    class AnnouncementType(TextChoices):
        SIMPLE = "simple", "SIMPLE"
        VIP = "vip", "VIP"

    class SellerTypeChoices(TextChoices):
        PRIVATE = "private", "PRIVATE"
        BUSINESS = "business", "BUSINESS"

    name = CharField(max_length=255)
    price = PositiveIntegerField()
    description = TextField(blank=True)
    category = ForeignKey('apps.Category', CASCADE, related_name='announcements')
    product_type = CharField(max_length=10, choices=AnnouncementType.choices, default=AnnouncementType.SIMPLE)
    attribute = JSONField(blank=True, null=True)
    seller_type = CharField(max_length=10,choices=SellerTypeChoices.choices, default=SellerTypeChoices.PRIVATE)
    user = ForeignKey("apps.User", CASCADE, related_name='announcements')

    @property
    def first_image(self):
        return self.favorites.count()
        # img = self.images.first()
        # if img:
        #     return img.image.url
        # return None


class AnnouncementImage(ImageBaseModel):
    product = ForeignKey('apps.Announcement', CASCADE, related_name='images')
