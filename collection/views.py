from .models import Collection, CollectionAccessRequest
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CollectionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q


def index(request):
    search_query = request.GET.get('search', '')

    search = Collection.objects.all()

    if search_query:
        # Filter collections by their name or by related game attributes
        search = search.filter(
            Q(name__icontains=search_query) |
            Q(games__title__icontains=search_query) |
            Q(games__description__icontains=search_query) |
            Q(games__genre__icontains=search_query) |
            Q(games__platform__icontains=search_query) |
            Q(games__location__icontains=search_query)
        ).distinct()

    # Add any additional filtering (e.g., for private collections) as needed
    if request.user.is_authenticated:
        collections = search.all()
    else:
        collections = search.filter(is_private=False)

    # Simply pass the collections directly
    return render(request, "collection/index.html", {
        "collections": collections
    })


@login_required
def create_collection(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, user=request.user)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.creator = request.user
            collection.save()
            form.save()
            messages.success(request, 'Collection created successfully!')
            return redirect('collection:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CollectionForm(user=request.user)

    return render(request, 'collection/create_collection.html', {'form': form})


def view_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    # Check if user has permission to view the collection
    has_access = (
        not collection.is_private or  # Public collections
        request.user == collection.creator or  # Collection creator
        request.user.userprofile.role == 'Librarian' or  # Librarians
        CollectionAccessRequest.objects.filter(  # Approved access request
            collection=collection,
            requester=request.user,
            status='approved'  # Changed from CollectionAccessRequest.APPROVED to match the model's status
        ).exists()
    )

    if not has_access:
        messages.error(request, 'You do not have permission to view this private collection.')
        return redirect('collection:index')

    return render(request, 'collection/view_collection.html', {'collection': collection})


@login_required
def edit_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    if collection.creator != request.user and request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to edit this collection.')
        return redirect('collection:index')

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Collection updated successfully!')
            return redirect('collection:view_collection', pk=collection.pk)
    else:
        form = CollectionForm(instance=collection, user=request.user)

    return render(request, 'collection/edit_collection.html',
                  {'form': form, 'collection': collection})


@login_required
def delete_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    if collection.creator != request.user and request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to delete this collection.')
        return redirect('collection:index')

    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'Collection deleted successfully!')
        return redirect('collection:index')

    return render(request, 'collection/delete_collection.html', {'collection': collection})


@login_required
def request_access(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    # Check if user already has a pending request
    existing_request = CollectionAccessRequest.objects.filter(
        collection=collection,
        requester=request.user,
        status='pending'  # Changed from CollectionAccessRequest.PENDING
    ).first()

    if existing_request:
        messages.info(request, 'You already have a pending request for this collection.')
        return redirect('collection:index')

    if request.method == 'POST':
        # Check for any existing request (including rejected ones)
        existing_request = CollectionAccessRequest.objects.filter(
            collection=collection,
            requester=request.user
        ).first()

        if existing_request:
            # If there's an existing request, update its status to PENDING
            existing_request.status = 'pending'  # Changed from CollectionAccessRequest.PENDING
            existing_request.save()
        else:
            # Create a new access request
            CollectionAccessRequest.objects.create(
                collection=collection,
                requester=request.user,
                status='pending'  # Changed from CollectionAccessRequest.PENDING
            )

        messages.success(request, 'Access request submitted successfully.')
        return redirect('collection:index')

    return redirect('collection:index')


@login_required
def manage_access_requests(request):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to manage access requests.')
        return redirect('catalog:index')

    pending_requests = CollectionAccessRequest.objects.filter(status='pending')
    return render(request, 'collection/manage_access_requests.html', {
        'pending_requests': pending_requests
    })


@login_required
def approve_request(request, request_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to approve requests.')
        return redirect('catalog:index')

    access_request = get_object_or_404(CollectionAccessRequest, id=request_id)
    access_request.status = 'approved'  # Changed from CollectionAccessRequest.APPROVED
    access_request.save()
    messages.success(request, 'Access request approved successfully.')
    return redirect('collection:manage_access_requests')


@login_required
def reject_request(request, request_id):
    if request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to reject requests.')
        return redirect('catalog:index')

    access_request = get_object_or_404(CollectionAccessRequest, id=request_id)
    access_request.status = 'rejected'  # Changed from CollectionAccessRequest.REJECTED
    access_request.save()
    messages.success(request, 'Access request rejected successfully.')
    return redirect('collection:manage_access_requests')
