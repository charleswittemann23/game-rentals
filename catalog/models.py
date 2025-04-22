from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
from datetime import timedelta
from django.core.exceptions import ValidationError


def calculate_upc_check_digit(upc_without_check_digit):
    total = 0
    for i, digit in enumerate(upc_without_check_digit):
        num = int(digit)
        total += num * 3 if i % 2 == 0 else num
    return str((10 - (total % 10)) % 10)


def generate_upc():
    while True:
        manufacturer = f"{random.randint(0, 999999):06d}"
        product = f"{random.randint(0, 99999):05d}"
        base_upc = manufacturer + product
        check_digit = calculate_upc_check_digit(base_upc)
        upc = base_upc + check_digit
        if not Game.objects.filter(upc=upc).exists():
            return upc


class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=100)
    platform = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='game_images/')
    upc = models.CharField(max_length=12, unique=True, blank=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.clean()
        if not self.upc:
            self.upc = generate_upc()
        super().save(*args, **kwargs)

    @property
    def is_in_private_collection(self):
        if self.pk is None:  # Check if object has an ID yet
            return False     # Return a default value when not yet saved
        return self.collections.filter(is_private=True).exists()

    @property
    def private_collection(self):
        return self.collections.filter(is_private=True).first()

    def clean(self):
        if self.is_in_private_collection and self.collections.count() > 1:
            raise ValidationError("A game in a private collection cannot be in any other collections.")

    @property
    def is_on_loan(self):
        return self.loans.filter(is_returned=False).exists()

    @property
    def current_borrower(self):
        active_loan = self.loans.filter(is_returned=False).first()
        return active_loan.borrower if active_loan else None

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(rating.rating for rating in ratings) / len(ratings)
        return 0

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

    DURATION_CHOICES = [
        (7, '1 Week'),
        (14, '2 Weeks'),
        (21, '3 Weeks'),
        (28, '4 Weeks'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='borrow_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    duration_days = models.IntegerField(choices=DURATION_CHOICES, default=14)
    request_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_requests')
    
    def __str__(self):
        return f"{self.requester.username}'s request for {self.game.title}"


class Loan(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    borrow_date = models.DateTimeField()
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.borrower.username}'s loan of {self.game.title}"


class Comment(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.game.title}'


class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['game', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f'Rating {self.rating} by {self.user.username} on {self.game.title}'
