from django.db import models


class Game(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='game_images/', default="/images/default.jpg")

    def __str__(self):
        return self.title
