from django.urls import path
from django.contrib.auth import views as auth_views

from music import views as music_views

urlpatterns = [
    # Landing
    path('', music_views.landing, name='landing'),

    # Auth
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    path(
        'register/',
        music_views.register,
        name='register'
    ),

    # Dashboard
    path(
        'dashboard/',
        music_views.dashboard,
        name='dashboard'
    ),

    # Yandex
    path(
        'yandex/connect/',
        music_views.yandex_connect,
        name='yandex_connect'
    ),
    path(
        'yandex/current/',
        music_views.yandex_current,
        name='yandex_current'
    ),

    # Spotify
    path(
        'spotify/connect/',
        music_views.spotify_connect,
        name='spotify_connect'
    ),
    path(
        'spotify/current/',
        music_views.spotify_current,
        name='spotify_current'
    ),

    path(
        'spotify/callback/',
        music_views.spotify_callback,
        name='spotify_callback'
    ),
]


