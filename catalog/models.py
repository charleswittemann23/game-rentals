from django.db import models

class Game(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)  # Optional image link

    def __str__(self):
        return self.title
