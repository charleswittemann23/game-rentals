from .models import Game
from django.shortcuts import render, redirect,get_object_or_404
from .forms import GameForm
from django.contrib.auth.decorators import login_required


def index(request):
    games = Game.objects.all()

    return render(request, "index.html", {
        "games": games,
    })


def game_detail(request, upc):
    game = get_object_or_404(Game, upc=upc)
    return render(request, 'game_detail.html', {'game': game})


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

    return render(request, 'add_game.html', {'form': form})
