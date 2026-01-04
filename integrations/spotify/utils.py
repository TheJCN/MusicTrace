from django.utils import timezone
from spotipy import SpotifyOAuth
from MusicTrace import settings


def get_valid_spotify_token(service):
    """
    Проверяет access_token и обновляет его при необходимости.
    Возвращает валидный access_token.
    """

    if service.expires_at and service.expires_at > timezone.now():
        return service.access_token

    oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
    )

    token_info = oauth.refresh_access_token(service.refresh_token)

    service.access_token = token_info["access_token"]
    service.expires_at = timezone.now() + timezone.timedelta(
        seconds=token_info["expires_in"]
    )

    if "refresh_token" in token_info:
        service.refresh_token = token_info["refresh_token"]

    service.save(update_fields=[
        "access_token",
        "refresh_token",
        "expires_at",
    ])

    return service.access_token