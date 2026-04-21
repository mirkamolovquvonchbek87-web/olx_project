from django.core.exceptions import ValidationError
from django.db.models import (
    CharField, CASCADE, ForeignKey, JSONField, TextChoices, Model, 
    UniqueConstraint, BooleanField, FloatField, EmailField
)
from django.db.models.fields import PositiveIntegerField, TextField, DateTimeField
from apps.models.base import ImageBaseModel, SlugBaseModel, CreatedBaseModel


class Announcement(SlugBaseModel, CreatedBaseModel):
    class AnnouncementType(TextChoices):
        SIMPLE = "simple", "SIMPLE"
        VIP = "vip", "VIP"

    class SellerTypeChoices(TextChoices):
        PRIVATE = "private", "PRIVATE"
        BUSINESS = "business", "BUSINESS"

    class Status(TextChoices):
        ACTIVE = 'active', 'Active'
        UNACTIVE = 'unactive', 'Unactive'
        UNPAID = 'unpaid', 'Unpaid'
        MODERATED = 'moderated', 'Moderated'
        WAITING = 'waiting', 'Waiting'

    name = CharField(max_length=155)
    category = ForeignKey('apps.Category', CASCADE, related_name='announcements')
    user = ForeignKey('apps.User', CASCADE, related_name='announcements')
    description = TextField(blank=True) # User requested CKEditor5Field, using TextField for now
    price_attribute = JSONField(blank=True, null=True)
    attribute = JSONField(blank=True, null=True)
    region = ForeignKey('apps.Region', CASCADE, related_name='announcements')
    district = ForeignKey('apps.District', CASCADE, related_name='announcements')
    
    # Location
    is_exact_locations = BooleanField(default=False)
    lat = FloatField(blank=True, null=True)
    lng = FloatField(blank=True, null=True)
    
    is_auto_extend = BooleanField(default=False)
    is_top = BooleanField(default=False)
    status = CharField(max_length=25, choices=Status.choices, default=Status.WAITING)
    published_at = DateTimeField(blank=True, null=True, editable=False)
    
    # Contact
    full_name = CharField(max_length=100)
    email = EmailField(blank=True, null=True)
    phone = CharField(max_length=15, blank=True, null=True)
    
    # Statistics
    phone_count = PositiveIntegerField(default=0)
    view_count = PositiveIntegerField(default=0)
    like_count = PositiveIntegerField(default=0)

    price = PositiveIntegerField()
    product_type = CharField(max_length=10, choices=AnnouncementType.choices, default=AnnouncementType.SIMPLE)
    seller_type = CharField(max_length=10, choices=SellerTypeChoices.choices, default=SellerTypeChoices.PRIVATE)



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

    def __str__(self):
        return f"{self.user} - {self.announcement}"


class ModeratedAnnouncement(Announcement):
    class Meta:
        proxy = True
        verbose_name = "Kutilayotgan E'lon"
        verbose_name_plural = "Moderatsiyadagi E'lonlar"