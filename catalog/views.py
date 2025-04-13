from .models import Game, BorrowRequest, Loan, Rating
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GameForm, CommentForm, RatingForm
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
    search_query = request.GET.get('search', '')
    
    if search_query:
        games = games.filter(title__icontains=search_query)
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

    
    return render(request, "index.html", {
        "games": games,
        "public_collections": public_collections,
    })


def game_detail(request, upc):
    game = get_object_or_404(Game, upc=upc)
    comments = game.comments.all()
    ratings = game.ratings.all()
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(game=game, user=request.user).first()
    
    if request.method == 'POST' and request.user.is_authenticated:
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.game = game
                comment.user = request.user
                comment.save()
                messages.success(request, 'Your comment has been added.')
                return redirect('catalog:game_detail', upc=game.upc)
        elif 'rating' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating, created = Rating.objects.update_or_create(
                    game=game,
                    user=request.user,
                    defaults={'rating': int(rating_form.cleaned_data['rating'])}
                )
                messages.success(request, 'Your rating has been saved.')
                return redirect('catalog:game_detail', upc=game.upc)
    else:
        comment_form = CommentForm()
        rating_form = RatingForm(instance=user_rating)
    
    return render(request, 'game_detail.html', {
        'game': game,
        'comments': comments,
        'ratings': ratings,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'user_rating': user_rating,
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

    return render(request, 'add_game.html', {'form': form})


@login_required
def request_borrow(request, game_id):
    if request.user.userprofile.role not in ['Patron', 'Librarian']:
        messages.error(request, 'Only patrons and librarians can borrow games.')
        return redirect('catalog:index')
    
    game = get_object_or_404(Game, id=game_id)
    
    # For Librarians, create loan directly
    if request.user.userprofile.role == 'Librarian':
        # Check if user already has this game on loan
        user_loan = Loan.objects.filter(
            game=game,
            borrower=request.user,
            is_returned=False
        ).first()
        
        if user_loan:
            messages.info(request, 'You already have this game on loan.')
            return redirect('catalog:index')
        
        # Check if game is already on loan to someone else
        active_loan = Loan.objects.filter(
            game=game,
            is_returned=False
        ).exclude(borrower=request.user).first()
        
        if active_loan:
            messages.info(request, 'This game is already on loan to another user.')
            return redirect('catalog:index')
        
        # Create loan directly for Librarians
        due_date = timezone.now() + timedelta(days=14)  # 2-week loan period
        Loan.objects.create(
            game=game,
            borrower=request.user,
            due_date=due_date
        )
        
        messages.success(request, 'Game borrowed successfully.')
        return redirect('catalog:index')
    
    # For Patrons, create borrow request
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
    if request.user.userprofile.role not in ['Patron', 'Librarian']:
        messages.error(request, 'Only patrons and librarians can view their loans.')
        return redirect('catalog:index')
    
    active_loans = Loan.objects.filter(
        borrower=request.user,
        is_returned=False
    ).order_by('-borrow_date')
    
    return render(request, 'my_loans.html', {
        'active_loans': active_loans
    })


@login_required
def manage_borrow_requests(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'Only librarians can manage borrow requests.')
        return redirect('catalog:index')
    
    pending_requests = BorrowRequest.objects.filter(status='pending').order_by('request_date')
    return render(request, 'manage_borrow_requests.html', {
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
    
    return render(request, 'edit_game.html', {
        'form': form,
        'game': game
    })


@login_required
@require_POST
def return_game(request, game_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'Only librarians can return games on behalf of users.')
        return redirect('catalog:index')
    
    game = get_object_or_404(Game, id=game_id)
    active_loan = Loan.objects.filter(game=game, is_returned=False).first()
    
    if not active_loan:
        messages.info(request, 'This game is not currently on loan.')
        return redirect('catalog:game_detail', upc=game.upc)
    
    active_loan.is_returned = True
    active_loan.return_date = timezone.now()
    active_loan.save()
    
    messages.success(request, f'Game has been returned from {active_loan.borrower.username}.')
    return redirect('catalog:game_detail', upc=game.upc)
