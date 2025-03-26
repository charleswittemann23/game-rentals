from .models import Game, Collection
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GameForm, CollectionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):
    games = Game.objects.all()
    if request.user.is_authenticated and request.user.userprofile.role == 'Librarian':
        collections = Collection.objects.all()
    else:
        collections = Collection.objects.filter(is_private=False)
    return render(request, "catalog/index.html", {
        "games": games,
        "public_collections": collections
    })


@login_required
def add_game(request):
    if request.user.userprofile.role != 'Librarian':
        return redirect('home:index')

    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog')
    else:
        form = GameForm()

    return render(request, 'catalog/add_game.html', {'form': form})


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
            return redirect('catalog')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CollectionForm(user=request.user)
    
    return render(request, 'catalog/create_collection.html', {'form': form})


@login_required
def edit_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    
    # Only allow creator to edit
    if collection.creator != request.user:
        messages.error(request, 'You do not have permission to edit this collection.')
        return redirect('catalog')
    
    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Collection updated successfully!')
            return redirect('catalog')
    else:
        form = CollectionForm(instance=collection, user=request.user)
    
    return render(request, 'catalog/edit_collection.html', {'form': form, 'collection': collection})


@login_required
def delete_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    
    # Only allow creator to delete
    if collection.creator != request.user:
        messages.error(request, 'You do not have permission to delete this collection.')
        return redirect('catalog')
    
    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'Collection deleted successfully!')
        return redirect('catalog')
    
    return render(request, 'catalog/delete_collection.html', {'collection': collection})
