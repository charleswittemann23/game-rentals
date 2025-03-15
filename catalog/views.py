from django.shortcuts import render
from .models import Game

def index(request):
    games = Game.objects.all()  # Get all games from the database
    return render(request, "catalog/index.html", {"games": games})
