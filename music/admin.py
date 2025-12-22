from django.contrib import admin
from .models import MusicService, Track, UserTrackActivity

# Сервисы
admin.site.register(MusicService)

# Сущности
admin.site.register(Track)
admin.site.register(UserTrackActivity)
