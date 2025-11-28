from django import forms
from django.contrib.auth.models import User
from .models import Resume

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

class UploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ["file"]

# forms.py
from django import forms
from .models import Application

class ApplyForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["full_name", "email", "phone", "cover_letter"]
