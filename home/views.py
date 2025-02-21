from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    if request.user.is_superuser:  # Check if user is an admin
        return render(request, "home/admin.html")
    else:
        return render(request, "home/index.html")

    # if request.user.is_authenticated:
    #     if request.user.groups.filter(name='Librarians').exists():
    #         role = 'librarian'
    #     else:
    #         role = 'user'
    # else:
    #     role = None

    return render(request, 'home/index.html', {'role': role})

@login_required
def dashboard(request):
    return render(request, "home/dashboard.html")
