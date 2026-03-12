from django.db.models import CharField, CASCADE, ManyToManyField, ForeignKey, JSONField, TextChoices, Model, ImageField
from django.db.models.fields import PositiveIntegerField, PositiveSmallIntegerField, TextField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from apps.models.base import ImageBaseModel, SlugBaseModel, CreatedBaseModel

#
# class Category(SlugBaseModel, ImageBaseModel, MPTTModel):
#     name = CharField(max_length=255)
#     parent = TreeForeignKey('self', CASCADE, null=True, blank=True, related_name='children')
#     attribute = JSONField(blank=True, null=True)
#
#     def __str__(self):
#         return self.name
#
#     class MPTTMeta:
#         order_insertion_by = ['name']



class Announcement(SlugBaseModel, CreatedBaseModel):
    class AnnouncementType(TextChoices):
        SIMPLE = "simple", "SIMPLE"
        VIP = "vip", "VIP"

    class SellerTypeChoices(TextChoices):
        PRIVATE = "private", "PRIVATE"
        BUSINESS = "business", "BUSINESS"

    name = CharField(max_length=255)
    price = PositiveIntegerField()
    discount = PositiveSmallIntegerField(db_default=0)
    description = TextField(blank=True)
    category = ForeignKey('apps.Category', CASCADE, related_name='products')
    product_type = CharField(max_length=10, choices=AnnouncementType.choices, default=AnnouncementType.SIMPLE)
    attribute = JSONField(blank=True, null=True)
    seller_type = CharField(max_length=10,choices=SellerTypeChoices.choices, default=SellerTypeChoices.PRIVATE)

    @property
    def first_image(self):
        return self.favorites.count()
        # img = self.images.first()
        # if img:
        #     return img.image.url
        # return None


class ProductImage(ImageBaseModel):
    image = ImageField(upload_to='products/%Y/%m/%d')
    product = ForeignKey('apps.Announcement', CASCADE, related_name='images')
