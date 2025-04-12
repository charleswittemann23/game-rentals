from .models import Game
from django.shortcuts import render, redirect
from .forms import GameForm
from django.contrib.auth.decorators import login_required
from collection.models import Collection, CollectionAccessRequest
from django.db.models import Q


def index(request):
    # Get all public collections
    public_collections = Collection.objects.filter(is_private=False)
    
    # Start with all games
    games = Game.objects.all()
    
    # If user is authenticated and not a Librarian, filter games based on access
    if request.user.is_authenticated and request.user.userprofile.role == 'Patron':
        # Get IDs of private collections the user has access to
        approved_requests = CollectionAccessRequest.objects.filter(
            requester=request.user,
            status='approved'
        ).values_list('collection_id', flat=True)
        
        # Filter games to show:
        # 1. Games from public collections
        # 2. Games from private collections the user has access to
        games = games.filter(
            Q(collections__is_private=False) |  # Public collections
            Q(collections__id__in=approved_requests)  # Private collections with approved access
        ).distinct()
    elif not request.user.is_authenticated:
        # For non-authenticated users, only show games from public collections
        games = games.filter(collections__is_private=False).distinct()
    else:
        # For Librarians, show all games
        games = games.distinct()

    # Debug print to check the number of games
    print(f"Number of games found: {games.count()}")
    print(f"Games: {list(games.values_list('title', flat=True))}")
    print(f"User role: {request.user.userprofile.role if request.user.is_authenticated else 'not authenticated'}")
    print(f"Approved requests: {list(approved_requests) if request.user.is_authenticated and request.user.userprofile.role == 'Patron' else 'N/A'}")

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
