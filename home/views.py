from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import ProfileForm
from django.urls import reverse


def index(request):
    username = None
    profileimage = None

    if request.user.is_authenticated:
        username = request.user.username
        try:
            profileimage = request.user.userprofile.profile_pic
        except:
            profileimage = "default"

    context = {
        'username': username,
        'profileimage': profileimage
    }

    return render(request, 'home/index.html', context)


def wishlist(request):
    return render(request, "home/wishlist.html")


@login_required
def update_user(request):
    if request.user.is_authenticated:
        profile_user, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'role': 'default_role',
                'profile_pic': 'images/default.jpg',
            }
        )

        if request.method == 'POST':
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile_user)

            if profile_form.is_valid():
                profile_form.save()
                return redirect(reverse('home:update_user'))
        else:
            profile_form = ProfileForm(instance=profile_user)

        return render(request, 'home/update_user.html', {'profile_form': profile_form})
