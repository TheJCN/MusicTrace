"""
Модели доменной области музыкального агрегатора.

Файл содержит основные сущности проекта:
- UserMusicService — подключённые музыкальные сервисы пользователя
- Track — универсальное представление музыкального трека
- UserTrackActivity — история музыкальной активности пользователей
"""
from django.db import models
from django.contrib.auth.models import User


class UserMusicService(models.Model):
    """
    Связь пользователя с музыкальным сервисом (Яндекс Музыка / Spotify).

    Сущность хранит данные, необходимые для доступа к API музыкального сервиса:
    - access token (обязателен)
    - refresh token и время истечения (используются для Spotify OAuth2)

    Один пользователь может быть подключён к каждому сервису только один раз.
    """

    SERVICE_CHOICES = (
        ('yandex', 'Yandex Music'),
        ('spotify', 'Spotify'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='music_services'
    )

    service = models.CharField(
        max_length=20,
        choices=SERVICE_CHOICES
    )

    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'service')

    def __str__(self):
        return f"{self.user.username} — {self.service}"


class Track(models.Model):
    """
    Универсальная сущность музыкального трека.

    Используется для хранения треков, полученных из разных музыкальных сервисов
    (Яндекс Музыка и Spotify), в едином формате.

    Поля модели представляют пересечение данных, доступных в обоих API,
    что позволяет использовать одну модель для агрегации статистики,
    истории прослушиваний и рекомендаций.
    """

    SERVICE_CHOICES = (
        ('yandex', 'Yandex Music'),
        ('spotify', 'Spotify'),
    )

    service = models.CharField(
        max_length=20,
        choices=SERVICE_CHOICES
    )

    external_id = models.CharField(max_length=255)

    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)

    track_url = models.URLField(blank=True)
    cover_url = models.URLField(blank=True)

    duration_ms = models.IntegerField()
    genre = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('service', 'external_id')
        indexes = [
            models.Index(fields=['service', 'external_id']),
        ]

    def __str__(self):
        return f"{self.artist} — {self.title}"


class UserTrackActivity(models.Model):
    """
    История взаимодействия пользователя с музыкальными треками.

    Сущность фиксирует факт взаимодействия пользователя с треком
    в определённый момент времени (played_at), независимо от источника
    данных (реальное воспроизведение, импорт из избранного и т.д.).

    Используется как основа для:
    - построения истории прослушиваний
    - отображения статистики
    - формирования рекомендаций
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='track_activities'
    )

    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='user_activities'
    )

    played_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'played_at']),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.track}"
