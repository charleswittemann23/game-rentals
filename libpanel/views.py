from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from collection.models import CollectionAccessRequest
from catalog.models import BorrowRequest, Loan
from datetime import timedelta
from django.utils import timezone
from django.db import transaction


@login_required
def users(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view.')
        return redirect('home:index')

    user = User.objects.all()

    return render(request, 'libpanel/users.html', {'users': user})


@login_required
def update_user(request, user_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to complete this action.')
        return redirect('home:index')

    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        new_role = request.POST.get('role')
        user.userprofile.role = new_role
        user.save()
    return redirect('libpanel:users')


@login_required
@require_POST
def approve_collection_access_request(request, request_id):
    access_request = get_object_or_404(CollectionAccessRequest, id=request_id)
    collection = access_request.collection

    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to approve this request.')
        return redirect('home:index')

    if access_request.status != CollectionAccessRequest.PENDING:
        messages.warning(request, 'This request has already been processed.')
        return redirect('libpanel:requests')

    try:
        unavailable_games = []

        with transaction.atomic():
            access_request.status = CollectionAccessRequest.APPROVED
            access_request.updated_at = timezone.now()
            access_request.save()

            # Optional: Add to shared_with if such a field exists
            if hasattr(collection, 'shared_with'):
                collection.shared_with.add(access_request.requester)

            for game in collection.games.all():
                is_on_loan = Loan.objects.filter(game=game, return_date__isnull=True).exists()
                if is_on_loan:
                    unavailable_games.append(game.title)
                    continue

                Loan.objects.create(
                    game=game,
                    borrower=access_request.requester,
                    borrow_date=timezone.now(),
                    due_date=timezone.now() + timedelta(days=14)
                )

        if unavailable_games:
            messages.warning(
                request,
                f'Request approved, but the following games are currently unavailable: {", ".join(unavailable_games)}.'
            )
        else:
            messages.success(request, 'Request approved')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('libpanel:requests')

@login_required
@require_POST
def reject_access_request(request, request_id):
    access_request = get_object_or_404(CollectionAccessRequest, id=request_id)
    collection = access_request.collection

    # Ensure only the collection's creator can reject requests
    if collection.creator != request.user:
        messages.error(request, 'You do not have permission to reject this request.')
        return redirect('home:index')

    if access_request.status != CollectionAccessRequest.PENDING:
        messages.warning(request, 'This request has already been processed.')
        return redirect('libpanel:requests')

    # Mark the request as rejected
    access_request.status = CollectionAccessRequest.REJECTED
    access_request.updated_at = timezone.now()
    access_request.save()

    messages.success(request, 'Collection access request rejected.')
    return redirect('libpanel:requests')

@login_required
@require_POST
def approve_borrow_request(request, request_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home:index')
    
    try:
        borrow_request = BorrowRequest.objects.get(id=request_id)
        borrow_request.status = 'approved'
        borrow_request.processed_by = request.user
        borrow_request.processed_date = timezone.now()
        borrow_request.save()
        
        # Create a new loan record using the requested duration
        loan = Loan.objects.create(
            game=borrow_request.game,
            borrower=borrow_request.requester,
            borrow_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=borrow_request.duration_days)
        )
        
        messages.success(request, 'Borrow request approved successfully.')
    except BorrowRequest.DoesNotExist:
        messages.error(request, 'Borrow request not found.')
    
    return redirect('libpanel:requests')


@login_required
@require_POST
def reject_borrow_request(request, request_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home:index')
    
    try:
        borrow_request = BorrowRequest.objects.get(id=request_id)
        borrow_request.status = 'rejected'
        borrow_request.save()
        messages.success(request, 'Borrow request rejected successfully.')
    except BorrowRequest.DoesNotExist:
        messages.error(request, 'Borrow request not found.')
    
    return redirect('libpanel:requests')


@login_required
def requests(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view.')
        return redirect('home:index')
    
    # Get pending collection access requests
    access_requests = CollectionAccessRequest.objects.filter(status='pending').order_by('created_at')
    
    # Get pending game borrow requests
    borrow_requests = BorrowRequest.objects.filter(status='pending').order_by('request_date')
    
    return render(request, "libpanel/requests.html", {
        'access_requests': access_requests,
        'borrow_requests': borrow_requests
    })

@login_required
def loans(request):
    if request.user.userprofile.role != 'Librarian':
        return redirect('home')

    all_active_loans = Loan.objects.filter(
        is_returned=False
    ).select_related('game', 'borrower')

    context = {
        'all_active_loans': all_active_loans,
    }

    return render(request, 'libpanel/loans.html', context)
