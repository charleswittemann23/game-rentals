from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def index(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view.')
        return redirect('home:index')
    return render(request, "index.html")


@login_required
def users(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view.')
        return redirect('home:index')

    user = User.objects.all()

    return render(request, 'users.html', {'users': user})


@login_required
def update_user(request, user_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to complete this action.')
        return redirect('home:index')

    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        new_role = request.POST.get('role')
        user.userprofile.role = new_role
        user.save()
    return redirect('users')


@login_required
def game_requests(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view.')
        return redirect('home:index')
    return render(request, "game_requests.html")


@login_required
def collection_requests(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view.')
        return redirect('home:index')
    return render(request, "collection_requests.html")
