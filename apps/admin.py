from django.contrib.admin import ModelAdmin
from django.contrib import admin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from apps.models import Category, Announcement


# Register your models here.
@admin.register(Category)
class CategoryModelAdmin(ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(Announcement)
class AnnouncementModelAdmin(ModelAdmin):
    pass




