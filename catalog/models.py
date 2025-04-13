from django.db import models
from django.utils import timezone
import random


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
    description = models.TextField(default='')
    release_date = models.DateField(default=timezone.now)
    genre = models.CharField(max_length=100, default='Unknown')
    platform = models.CharField(max_length=100, default='Unknown')
    image = models.ImageField(upload_to='game_images/')
    upc = models.CharField(max_length=12, unique=True, blank=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.upc:
            self.upc = generate_upc()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
