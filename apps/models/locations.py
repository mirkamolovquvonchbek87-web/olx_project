

from django.db.models import ForeignKey, CASCADE, Model, FloatField, CharField

class Region(Model):
    name = CharField(max_length=255)
    lat = FloatField()
    lng = FloatField()

    def __str__(self):
        return self.name

class District(Model):
    name = CharField(max_length=255)
    lat = FloatField()
    lng = FloatField()
    region = ForeignKey('apps.Region', CASCADE, related_name='districts')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

