from .models import Game
from django.shortcuts import render, redirect
from .forms import GameForm
from django.contrib.auth.decorators import login_required


def index(request):
    games = Game.objects.all()
    return render(request, "catalog/index.html", {"games": games})


@login_required
def add_game(request):
    if request.user.userprofile.role != 'Librarian':
        return redirect('home:index')

    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog')
    else:
        form = GameForm()

    return render(request, 'catalog/add_game.html', {'form': form})
