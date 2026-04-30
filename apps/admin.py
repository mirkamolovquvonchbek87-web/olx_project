from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from apps.models import User, Category, Announcement, Chat, Message, Region, District, Transaction
from apps.models.announcements import AnnouncementImage, FavouriteAnnouncement, ModeratedAnnouncement


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'transaction_type', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['user__username', 'description']


# Inlines
class AnnouncementImageTabularInline(TabularInline):
    model = AnnouncementImage
    extra = 1


class MessageTabularInline(TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['created_at']


class DistrictTabularInline(TabularInline):
    model = District
    extra = 1


# ModelAdmins
@admin.register(User)
class UserModelAdmin(ModelAdmin):
    list_display = ['email', 'first_name', 'phone', 'balance', 'is_staff']
    search_fields = ['email', 'first_name', 'phone']
    list_filter = ['is_staff', 'is_active', 'is_superuser']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('email', 'password', 'first_name', 'last_name', 'phone', 'avatar')
        }),
        ('Balans', {
            'fields': ('balance', 'bonus')
        }),
        ('Huquqlar va Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Muhim sanalar', {
            'fields': ('last_login', 'date_joined')
        }),
    )


@admin.register(Category)
class CategoryModelAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    search_fields = ['name', 'slug']
    list_filter = ['parent']
    prepopulated_fields = {'slug': ('name',)}
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(Announcement)
class AnnouncementModelAdmin(ModelAdmin):
    list_display = ['name', 'price', 'status', 'user', 'category', 'view_count', 'created_at']
    search_fields = ['name', 'description', 'full_name', 'email', 'phone']
    list_filter = ['status', 'is_top', 'category', 'region', 'product_type', 'seller_type']
    readonly_fields = ['view_count', 'phone_count', 'like_count', 'created_at', 'updated_at', 'slug', 'published_at']
    inlines = [AnnouncementImageTabularInline]
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('name', 'slug', 'description', 'category', 'user', 'status', 'published_at')
        }),
        ('Narx va Atributlar', {
            'fields': ('price', 'price_attribute', 'attribute', 'product_type', 'seller_type')
        }),
        ('Joylashuv', {
            'fields': ('region', 'district', 'is_exact_locations', 'lat', 'lng')
        }),
        ('Aloqa Ma\'lumotlari', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Promouter (Top/Auto)', {
            'fields': ('is_top', 'is_auto_extend')
        }),
        ('Statistika', {
            'fields': ('view_count', 'phone_count', 'like_count', 'created_at', 'updated_at')
        }),
    )

    def image_thumbnail(self, obj):
        first_img = obj.images.first()
        if first_img and first_img.image:
            from django.utils.safestring import mark_safe
            return mark_safe(f'<img src="{first_img.image.url}" width="50" height="50" style="object-fit: cover;" />')
        return "-"
    image_thumbnail.short_description = "Rasm"

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Announcement.objects.get(pk=obj.pk)
            if old_obj.status != obj.status and obj.status == Announcement.Status.ACTIVE:
                from django.utils import timezone
                obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ModeratedAnnouncement)
class ModeratedAnnouncementAdmin(AnnouncementModelAdmin):
    list_display = ['image_thumbnail', 'name', 'price', 'status', 'user', 'category', 'created_at']
    actions = ['make_active', 'make_moderated', 'make_rejected']
    list_editable = ['status']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            status__in=[Announcement.Status.WAITING, Announcement.Status.MODERATED]
        )

    @admin.action(description="Tanlanganlarni Active (Faol) qilish")
    def make_active(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status=Announcement.Status.ACTIVE, published_at=timezone.now())
        self.message_user(request, f"{updated} ta e'lon faollashtirildi.")

    @admin.action(description="Tanlanganlarni Moderatsiyaga o'tkazish")
    def make_moderated(self, request, queryset):
        updated = queryset.update(status=Announcement.Status.MODERATED)
        self.message_user(request, f"{updated} ta e'lon moderatsiyaga o'tkazildi.")

    @admin.action(description="Tanlanganlarni Rad etish (Unactive)")
    def make_rejected(self, request, queryset):
        updated = queryset.update(status=Announcement.Status.UNACTIVE)
        self.message_user(request, f"{updated} ta e'lon rad etildi.")


@admin.register(Chat)
class ChatModelAdmin(ModelAdmin):
    list_display = ['user1', 'user2', 'announcement', 'created_at']
    search_fields = ['user1__email', 'user2__email', 'announcement__name']
    inlines = [MessageTabularInline]


@admin.register(Message)
class MessageModelAdmin(ModelAdmin):
    list_display = ['from_user', 'chat', 'is_read', 'created_at']
    search_fields = ['message', 'from_user__email']
    list_filter = ['is_read', 'created_at']


@admin.register(Region)
class RegionModelAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [DistrictTabularInline]


@admin.register(District)
class DistrictModelAdmin(ModelAdmin):
    list_display = ['name', 'region']
    search_fields = ['name']
    list_filter = ['region']


@admin.register(FavouriteAnnouncement)
class FavouriteAnnouncementModelAdmin(ModelAdmin):
    list_display = ['user', 'announcement', 'created_at']
    search_fields = ['user__email', 'announcement__name']
    list_filter = ['created_at']


@admin.register(AnnouncementImage)
class AnnouncementImageModelAdmin(ModelAdmin):
    list_display = ['id', 'product', 'image']
    list_filter = ['product']




