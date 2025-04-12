from .models import Game
from django.shortcuts import render, redirect
from .forms import GameForm
from django.contrib.auth.decorators import login_required
from collection.models import Collection


def index(request):
    # Get all public collections
    public_collections = Collection.objects.filter(is_private=False)
    
    # Get all games that belong to collections
    games = Game.objects.filter(collections__isnull=False)

    return render(request, "catalog/index.html", {
        "games": games,
        "public_collections": public_collections,
    })


@login_required
def add_game(request):
    if request.user.userprofile.role != 'Librarian':
        return redirect('home:index')

    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog:index')
    else:
        form = GameForm()

    return render(request, 'catalog/add_game.html', {'form': form})
