from django.contrib import admin
from .models import UserMusicService, Track, UserTrackActivity

# Сервисы
admin.site.register(UserMusicService)

# Сущности
admin.site.register(UserTrackActivity)
@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'artist',
        'service',
        'genre',
        'duration_ms',
        'created_at',
    )

    list_filter = (
        'service',
        'genre',
    )

    search_fields = (
        'title',
        'artist',
        'genre',
    )

    ordering = ('service', 'genre', 'artist', 'title')
