from django.db import models


class MusicService(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Track(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    duration_ms = models.IntegerField()
    genre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.artist} — {self.title}"

from django.contrib.auth.models import User


class UserTrackActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)
    is_liked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.track}"
