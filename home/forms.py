from django import forms
from .models import UserProfile
from django.contrib.auth.models import User

class ProfilePicForm(forms.ModelForm):
    profile_image = forms.ImageField(label="Profile Picture")
    class Meta:
        model= UserProfile
        fields= ('profile_pic',)
     