from django.core.exceptions import ValidationError
from django.db.models import CharField, CASCADE, ForeignKey, JSONField, TextChoices, Model, UniqueConstraint
from django.db.models.fields import PositiveIntegerField, PositiveSmallIntegerField, TextField, DateTimeField
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
    region = ForeignKey('apps.Region', CASCADE, related_name='announcements')
    district = ForeignKey('apps.District', CASCADE, related_name='announcements', null=True, blank=True)
    product_type = CharField(max_length=10, choices=AnnouncementType.choices, default=AnnouncementType.SIMPLE)
    attribute = JSONField(blank=True, null=True)
    seller_type = CharField(max_length=10,choices=SellerTypeChoices.choices, default=SellerTypeChoices.PRIVATE)
    user = ForeignKey("apps.User", CASCADE, related_name='announcements')
    views_count = PositiveIntegerField(default=0)
    phone_count = PositiveIntegerField(default=0)


    @property
    def first_image(self):
        return self.favorites.count()
        # img = self.images.first()
        # if img:
        #     return img.image.url
        # return None


class AnnouncementImage(ImageBaseModel):
    product = ForeignKey('apps.Announcement', CASCADE, related_name='images')


class FavouriteAnnouncement(Model):
    user = ForeignKey('apps.User', CASCADE, related_name='favourites')
    announcement = ForeignKey('apps.Announcement', CASCADE, related_name='favorites')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'announcement'], name='unique_favourite')
        ]
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        LIMIT = 150
        if self.pk is None:
            count = FavouriteAnnouncement.objects.filter(user=self.user).count()
            if count >= LIMIT:
                raise ValidationError(
                    f"Siz maksimal {LIMIT} ta sevimli e'longa ega bo'la olasiz."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def str(self):
        return f"{self.user} → {self.announcement}"