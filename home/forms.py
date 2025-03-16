from django import forms
from .models import UserProfile
from django.contrib.auth.models import User

class ProfilePicForm(forms.ModelForm):
    class Meta:
        model= UserProfile
        fields= ('profile_pic',)
