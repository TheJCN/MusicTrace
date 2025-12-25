from django.urls import path, include
from .views import connect_yandex, yandex_now_playing

urlpatterns = [
    path("connect/yandex/", connect_yandex, name="connect_yandex"),
    path("yandex/now-playing/", yandex_now_playing, name="yandex_now_playing"),
    path('accounts/', include('django.contrib.auth.urls')),
]
