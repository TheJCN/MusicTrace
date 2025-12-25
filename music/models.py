from django.db import models
from django.contrib.auth.models import User


class Track(models.Model):
    external_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    duration_ms = models.IntegerField()
    genre = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.artist} — {self.title}"


class UserMusicService(models.Model):
    SERVICE_CHOICES = (
        ('yandex', 'Yandex Music'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    access_token = models.TextField()

    class Meta:
        unique_together = ('user', 'service')

    def __str__(self):
        return f"{self.user.username} - {self.service}"


class UserTrackActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.track}"
