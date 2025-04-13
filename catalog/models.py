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


class BorrowRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='borrow_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    request_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_requests')
    
    def __str__(self):
        return f"{self.requester.username}'s request for {self.game.title}"


class Loan(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.borrower.username}'s loan of {self.game.title}"
