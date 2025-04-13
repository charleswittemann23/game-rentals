from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from collection.models import CollectionAccessRequest
from catalog.models import BorrowRequest, Loan
from datetime import timedelta
from django.utils import timezone


@login_required
def index(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view.')
        return redirect('home:index')
    return render(request, "libpanel/index.html")


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
def game_requests(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view.')
        return redirect('home:index')
    
    # Get pending borrow requests
    borrow_requests = BorrowRequest.objects.filter(status='PENDING').order_by('request_date')
    
    return render(request, "libpanel/game_requests.html", {
        'borrow_requests': borrow_requests
    })


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
        
        # Create a new loan record
        loan = Loan.objects.create(
            game=borrow_request.game,
            borrower=borrow_request.requester,
            borrow_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=14)  # 2-week loan period
        )
        
        messages.success(request, 'Borrow request approved successfully.')
    except BorrowRequest.DoesNotExist:
        messages.error(request, 'Borrow request not found.')
    
    return redirect('libpanel:collection_requests')


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
    
    return redirect('libpanel:collection_requests')


@login_required
def collection_requests(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view.')
        return redirect('home:index')
    
    # Get pending collection access requests
    access_requests = CollectionAccessRequest.objects.filter(status='PENDING').order_by('created_at')
    
    # Get pending game borrow requests
    borrow_requests = BorrowRequest.objects.filter(status='pending').order_by('request_date')
    
    return render(request, "libpanel/collection_requests.html", {
        'access_requests': access_requests,
        'borrow_requests': borrow_requests
    })
