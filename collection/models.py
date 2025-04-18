from django.contrib.auth.models import User
from django.db import models
from catalog.models import Game
from django.utils import timezone
from django.core.exceptions import ValidationError


class Collection(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    games = models.ManyToManyField(Game, related_name='collections')
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.creator.username}"

    def can_add_game(self, game):
        # If the game is already in a private collection, it can't be added to any other collection
        if game.is_in_private_collection:
            return False
        # If this collection is private and the game is in any other collection, it can't be added
        if self.is_private and game.collections.exists():
            return False
        return True

    def add_game(self, game):
        if not self.can_add_game(game):
            raise ValidationError("Cannot add game to collection. Game is already in a private collection or this is a private collection and the game is in another collection.")
        self.games.add(game)

    def save(self, *args, **kwargs):
        # If this collection is being made private, ensure none of its games are in other collections
        if self.is_private and self.pk:  # Only check for existing collections
            for game in self.games.all():
                if game.collections.exclude(pk=self.pk).exists():
                    raise ValidationError(f"Cannot make collection private. Game '{game.title}' is already in another collection.")
        super().save(*args, **kwargs)

class CollectionAccessRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='access_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['collection', 'requester']
        
    def __str__(self):
        return f"{self.requester.username}'s request for {self.collection.name}"
