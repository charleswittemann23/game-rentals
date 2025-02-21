from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile


@login_required
def index(request):
    role = "Patron"

    # if request.user.is_superuser:  # Check if user is an admin
    #     return render(request, "home/admin.html")
    # else:
    #     return render(request, "home/index.html")

    if request.user.is_authenticated:
        try:
            # Retrieve role from UserProfile
            role = request.user.userprofile.role
            username = request.user.username
        except UserProfile.DoesNotExist:
            role = "Guest"  # If UserProfile is missing

    return render(request, 'home/index.html', {'role': role, 'username': username})

@login_required
def dashboard(request):
    return render(request, "home/dashboard.html")

