from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib import admin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from apps.models import Category, Announcement
from apps.models.announcements import AnnouncementImage


# Register your models here.
@admin.register(Category)
class CategoryModelAdmin(ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }


class AnnouncementImageTabularInline(TabularInline):
    model = AnnouncementImage
    min_num = 1
    extra = 0


@admin.register(Announcement)
class AnnouncementModelAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = AnnouncementImageTabularInline,




@admin.register(AnnouncementImage)
class AnnouncementImagesModelAdmin(ModelAdmin):
    pass




