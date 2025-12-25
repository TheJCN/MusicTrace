from django.contrib import admin
from .models import UserMusicService, Track, UserTrackActivity

# Сервисы
admin.site.register(UserMusicService)

# Сущности
admin.site.register(Track)
admin.site.register(UserTrackActivity)
