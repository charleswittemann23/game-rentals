from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests

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
        except UserProfile.DoesNotExist:
            role = "Guest"  # If UserProfile is missing

    return render(request, 'home/index.html', {'role': role, 'username': username})

@login_required
def dashboard(request):
    return render(request, "home/dashboard.html")

