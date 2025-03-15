from .models import Game
from django.shortcuts import render, redirect
from .forms import GameForm
from django.contrib.auth.decorators import login_required

def index(request):
    games = Game.objects.all()  # Get all games from the database
    return render(request, "catalog/index.html", {"games": games})

@login_required
def add_game(request):
    if request.user.userprofile.role != 'Librarian':  # Check if the user has the 'Librarian' role
        return redirect('home:index')  # Redirect to the homepage or any other page if not a librarian

    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)  # Allow for image upload
        if form.is_valid():
            form.save()
            return redirect('catalog')  # Redirect to the catalog after saving the game
    else:
        form = GameForm()

    return render(request, 'catalog/add_game.html', {'form': form})

