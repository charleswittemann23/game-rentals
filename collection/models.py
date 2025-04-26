from django.contrib.auth.models import User
from django.db import models
from catalog.models import Game
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

    def add_game(self, game):
        if game.collections.filter(is_private=True).exclude(id=self.id).exists():
            raise ValidationError("Cannot add game to collection. Game is already in a private collection.")

        self.games.add(game)

        # If adding to a private collection, remove from all other collections
        if self.is_private:
            for collection in game.collections.exclude(id=self.id):
                collection.games.remove(game)

    def save(self, *args, **kwargs):
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
