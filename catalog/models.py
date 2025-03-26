from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(default='')
    release_date = models.DateField(default=timezone.now)
    genre = models.CharField(max_length=100, default='Unknown')
    platform = models.CharField(max_length=100, default='Unknown')
    image = models.ImageField(upload_to='game_images/')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

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
