from .models import Collection
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CollectionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):
    collections = Collection.objects.all()

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
            form.save_m2m()  # Save the many-to-many relationships
            messages.success(request, 'Collection created successfully!')
            return redirect('collection')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CollectionForm(user=request.user)

    return render(request, 'collection/create_collection.html', {'form': form})


@login_required
def view_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    if collection.is_private and collection.creator != request.user and request.user.userprofile.role != 'Librarian':
        messages.error(request, 'You do not have permission to view this private collection.')
        return redirect('catalog')

    return render(request, 'collection/view_collection.html', {'collection': collection})


@login_required
def edit_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    # Only allow creator to edit
    if collection.creator != request.user:
        messages.error(request, 'You do not have permission to edit this collection.')
        return redirect('collection')

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Collection updated successfully!')
            return redirect('collection')
    else:
        form = CollectionForm(instance=collection, user=request.user)

    return render(request, 'collection/edit_collection.html',
                  {'form': form, 'collection': collection})


@login_required
def delete_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    # Only allow creator to delete
    if collection.creator != request.user:
        messages.error(request, 'You do not have permission to delete this collection.')
        return redirect('collection')

    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'Collection deleted successfully!')
        return redirect('collection')

    return render(request, 'collection/delete_collection.html',
                  {'collection': collection})
