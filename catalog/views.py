from .models import Game, BorrowRequest, Loan, Rating, Comment
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GameForm, CommentForm, RatingForm, BorrowRequestForm
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
        games = games.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(genre__icontains=search_query) |
            Q(platform__icontains=search_query) |
            Q(location__icontains=search_query)
        )

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
    user_comment = None
    user_has_commented = False

    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(game=game, user=request.user).first()
        try:
            user_comment = Comment.objects.get(game=game, user=request.user)
            user_has_commented = True
        except Comment.DoesNotExist:
            pass

    if request.method == 'POST' and request.user.is_authenticated:
        if 'comment' in request.POST:
            if user_has_commented:
                # Update existing comment
                comment_form = CommentForm(request.POST, instance=user_comment)
                if comment_form.is_valid():
                    comment_form.save()
                    messages.success(request, 'Your comment has been updated.')
            else:
                # Create new comment
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
        comment_form = CommentForm(instance=user_comment)
        rating_form = RatingForm(instance=user_rating)

    return render(request, 'game_detail.html', {
        'game': game,
        'comments': comments,
        'ratings': ratings,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'user_rating': user_rating,
        'user_has_commented': user_has_commented,
        'user_comment': user_comment,
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
def request_borrow(request, upc):
    game = get_object_or_404(Game, upc=upc)
    
    # Check if game is available
    if game.is_on_loan:
        messages.error(request, 'This game is not available for borrowing.')
        return redirect('catalog:game_detail', upc=game.upc)
    
    # Check if user already has an active loan for this game
    if Loan.objects.filter(game=game, borrower=request.user, is_returned=False).exists():
        messages.error(request, 'You already have an active loan for this game.')
        return redirect('catalog:game_detail', upc=game.upc)
    
    # Check if user already has a pending request for this game
    if BorrowRequest.objects.filter(game=game, requester=request.user, status='pending').exists():
        messages.error(request, 'You already have a pending request for this game.')
        return redirect('catalog:game_detail', upc=game.upc)
    
    if request.method == 'POST':
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
            # Create the borrow request
            borrow_request = BorrowRequest.objects.create(
                game=game,
                requester=request.user,
                duration_days=form.cleaned_data['duration_days']
            )
            messages.success(request, 'Your borrow request has been submitted successfully.')
            return redirect('catalog:game_detail', upc=game.upc)
    else:
        form = BorrowRequestForm()
    
    return render(request, 'catalog/request_borrow.html', {
        'game': game,
        'form': form
    })


@login_required
def my_loans(request):
    # Get active loans for the current user
    active_loans = Loan.objects.filter(
        borrower=request.user,
        is_returned=False
    ).select_related('game')
    
    context = {
        'active_loans': active_loans,
    }
    
    return render(request, 'my_loans.html', context)


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
    
    # Create new loan using the requested duration
    borrow_date = timezone.now()
    due_date = borrow_date + timedelta(days=borrow_request.duration_days)
    Loan.objects.create(
        game=borrow_request.game,
        borrower=borrow_request.requester,
        borrow_date=borrow_date,
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
def delete_game(request, upc):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to delete games.')
        return redirect('catalog:index')
    
    game = get_object_or_404(Game, upc=upc)
    
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
def edit_game(request, upc):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to edit games.')
        return redirect('catalog:index')
    
    game = get_object_or_404(Game, upc=upc)
    
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, 'Game updated successfully.')
            return redirect('catalog:game_detail', upc=game.upc)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = GameForm(instance=game)
    
    return render(request, 'edit_game.html', {
        'form': form,
        'game': game
    })


@login_required
def return_game(request, upc):
    game = get_object_or_404(Game, upc=upc)
    
    # Check if game is on loan
    if not game.is_on_loan:
        messages.error(request, 'This game is not currently on loan.')
        return redirect('catalog:game_detail', upc=game.upc)
    
    # Get the active loan
    loan = Loan.objects.get(game=game, is_returned=False)
    
    # Check if user is the borrower or a librarian
    if request.user != loan.borrower and request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You are not authorized to return this game.')
        return redirect('catalog:game_detail', upc=game.upc)
    
    if request.method == 'POST':
        # Mark loan as returned
        loan.is_returned = True
        loan.return_date = timezone.now()
        loan.save()
        
        if request.user.userprofile.role == 'Librarian':
            messages.success(request, f'Game has been returned by {loan.borrower.get_full_name() or loan.borrower.username}.')
        else:
            messages.success(request, 'Game has been returned successfully.')
        
        return redirect('catalog:game_detail', upc=game.upc)
    
    return render(request, 'catalog/return_game.html', {'game': game})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Check if the user is the comment author or a librarian
    if request.user.userprofile.role == 'Librarian' or request.user == comment.user:
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this comment.')

    return redirect('catalog:game_detail', upc=comment.game.upc)
