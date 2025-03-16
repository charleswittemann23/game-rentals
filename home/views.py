from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import ProfilePicForm
from django.urls import reverse
from io import BytesIO

from django.core.files.storage import default_storage
from rest_framework.decorators import api_view
from rest_framework.response import Response





@login_required
def index(request):
    role = "Patron"
    username = request.user.username

    # if request.user.is_superuser:  # Check if user is an admin
    #     return render(request, "home/admin.html")
    # else:
    #     return render(request, "home/index.html")

    if request.user.is_authenticated:
        try:
            # Retrieve role from UserProfile
            role = request.user.userprofile.role
            profileimage = request.user.userprofile.profile_pic
        except UserProfile.DoesNotExist:
            role = "Guest"  # If UserProfile is missing
            profileimage="default"

    return render(request, 'home/index.html', {'role': role, 'username': username, 'profileimage': profileimage })


def wishlist(request):
    return render(request, "home/wishlist.html")
    
def update_user(request):
    if request.user.is_authenticated:
        profile_user, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
        'role': 'default_role',
        'profile_pic': 'images/default.jpg',
        # Add other default fields here
    }
)

        profile_form= ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)

        if profile_form.is_valid():
            profile_form.save()
            return redirect(reverse('home:index'))
        return render(request, 'home/update_user.html' ,{'profile_form': profile_form})




