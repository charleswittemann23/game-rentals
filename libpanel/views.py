from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def index(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view this private collection.')
        return redirect('home:index')
    return render(request, "libpanel/index.html")
