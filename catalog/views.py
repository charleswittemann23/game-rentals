from .models import Game, BorrowRequest, Loan
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GameForm
from django.contrib.auth.decorators import login_required
from collection.models import Collection, CollectionAccessRequest
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.views.decorators.http import require_POST


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
        # 1. Games that are in public collections
        # 2. Games that are in private collections the user has access to
        # 3. Games that are not in any collection
        games = games.filter(
            Q(collections__is_private=False) |  # Public collections
            Q(collections__id__in=approved_requests) |  # Private collections with access
            ~Q(collections__isnull=False)  # Games not in any collection
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

    return render(request, "index.html", {
        "games": games,
        "public_collections": public_collections,
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
            return redirect('catalog:index')
    else:
        form = GameForm()

    return render(request, 'catalog/add_game.html', {'form': form})


@login_required
def request_borrow(request, game_id):
    if request.user.userprofile.role != 'Patron':
        messages.error(request, 'Only patrons can request to borrow games.')
        return redirect('catalog:index')
    
    game = get_object_or_404(Game, id=game_id)
    
    # Check if user already has a pending request for this game
    existing_request = BorrowRequest.objects.filter(
        game=game,
        requester=request.user,
        status='pending'
    ).first()
    
    if existing_request:
        messages.info(request, 'You already have a pending request for this game.')
        return redirect('catalog:index')
    
    # Check if user already has an active loan for this game
    active_loan = Loan.objects.filter(
        game=game,
        borrower=request.user,
        is_returned=False
    ).first()
    
    if active_loan:
        messages.info(request, 'You already have this game on loan.')
        return redirect('catalog:index')
    
    # Create new borrow request
    BorrowRequest.objects.create(
        game=game,
        requester=request.user,
        status='pending'
    )
    
    messages.success(request, 'Borrow request submitted successfully.')
    return redirect('catalog:index')


@login_required
def my_loans(request):
    if request.user.userprofile.role != 'Patron':
        messages.error(request, 'Only patrons can view their loans.')
        return redirect('catalog:index')
    
    active_loans = Loan.objects.filter(
        borrower=request.user,
        is_returned=False
    ).order_by('-borrow_date')
    
    return render(request, 'catalog/my_loans.html', {
        'active_loans': active_loans
    })


@login_required
def manage_borrow_requests(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'Only librarians can manage borrow requests.')
        return redirect('catalog:index')
    
    pending_requests = BorrowRequest.objects.filter(status='pending').order_by('request_date')
    return render(request, 'catalog/manage_borrow_requests.html', {
        'pending_requests': pending_requests
    })


@login_required
def approve_borrow_request(request, request_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'Only librarians can approve borrow requests.')
        return redirect('catalog:index')
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if game is already on loan
    active_loan = Loan.objects.filter(
        game=borrow_request.game,
        is_returned=False
    ).first()
    
    if active_loan:
        messages.error(request, 'This game is already on loan to another patron.')
        return redirect('catalog:manage_borrow_requests')
    
    # Create new loan
    due_date = timezone.now() + timedelta(days=14)  # 2-week loan period
    Loan.objects.create(
        game=borrow_request.game,
        borrower=borrow_request.requester,
        due_date=due_date
    )
    
    # Update borrow request
    borrow_request.status = 'approved'
    borrow_request.processed_date = timezone.now()
    borrow_request.processed_by = request.user
    borrow_request.save()
    
    messages.success(request, 'Borrow request approved successfully.')
    return redirect('catalog:manage_borrow_requests')


@login_required
def reject_borrow_request(request, request_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'Only librarians can reject borrow requests.')
        return redirect('catalog:index')
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    borrow_request.status = 'rejected'
    borrow_request.processed_date = timezone.now()
    borrow_request.processed_by = request.user
    borrow_request.save()
    
    messages.success(request, 'Borrow request rejected successfully.')
    return redirect('catalog:manage_borrow_requests')


@login_required
@require_POST
def delete_game(request, game_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to delete games.')
        return redirect('catalog:index')
    
    game = get_object_or_404(Game, id=game_id)
    
    # Check if the game has any active loans
    if Loan.objects.filter(game=game, is_returned=False).exists():
        messages.error(request, 'Cannot delete a game that is currently on loan.')
        return redirect('catalog:index')
    
    # Delete any associated borrow requests
    BorrowRequest.objects.filter(game=game).delete()
    
    # Delete the game
    game.delete()
    messages.success(request, 'Game deleted successfully.')
    
    return redirect('catalog:index')


@login_required
def edit_game(request, game_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to edit games.')
        return redirect('catalog:index')
    
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, 'Game updated successfully.')
            return redirect('catalog:index')
    else:
        form = GameForm(instance=game)
    
    return render(request, 'catalog/edit_game.html', {
        'form': form,
        'game': game
    })
