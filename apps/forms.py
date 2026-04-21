import json
from django.forms import ModelForm, CharField, EmailField
from django.core.exceptions import ValidationError
from .models import Announcement, User
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class AnnouncementModelForm(ModelForm):

    seller_type = CharField(required=False)
    attribute = CharField(required=False)

    class Meta:
        model = Announcement
        fields = [
            'name', 'description', 'category', 'price', 
            'region', 'district', 'seller_type', 
            'full_name', 'email', 'phone'
        ]

    def clean_attribute(self):
        raw_attr = self.cleaned_data.get("attribute")

        if not raw_attr:
            return {}

        try:
            return json.loads(raw_attr)
        except Exception:
            raise ValidationError("Attribute JSON noto‘g‘ri")

    def clean(self):
        cleaned_data = super().clean()

        seller_type = cleaned_data.get("seller_type")

        if not seller_type:
            cleaned_data["seller_type"] = "private"
            
        phone = cleaned_data.get("phone")
        if phone:
            cleaned_data["phone"] = phone.replace(" ", "")

        return cleaned_data

class RegisterModelForm(ModelForm):
    email = EmailField()
    password = CharField(max_length=128)

    class Meta:
        model = User
        fields = ['email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Bunaqa pochta ro'yhatdan o'tgan")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user



class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")