from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Librarians').exists():
            role = 'librarian'
        else:
            role = 'user'
    else:
        role = None

    return render(request, 'home/index.html', {'role': role})
