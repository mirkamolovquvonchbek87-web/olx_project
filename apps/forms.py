from django import forms
from django_json_widget.widgets import JSONEditorWidget
from models import Category


class YourForm(forms.ModelForm):
    class Meta:
        model = Category

        fields = ('jsonfield',)

        widgets = {
            'jsonfield': JSONEditorWidget
        }
