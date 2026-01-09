from django.urls import path
from django.contrib.auth import views as auth_views
from music import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("register/", views.register, name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),


    path("yandex/connect/", views.yandex_connect, name="yandex_connect"),
    path("spotify/connect/", views.spotify_connect, name="spotify_connect"),
    path("spotify/callback/", views.spotify_callback, name="spotify_callback"),

    path("track/<int:track_id>/lyrics/", views.track_lyrics, name="track_lyrics"),

    path("api/now-playing/", views.api_now_playing),
    path("api/stats/summary/", views.api_stats_summary),
    path("api/stats/recent/", views.api_stats_recent),
    path("api/stats/activity/", views.api_stats_activity),
    path("api/user/services/", views.api_user_services),
]