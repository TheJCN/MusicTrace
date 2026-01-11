from asgiref.sync import sync_to_async
from integrations.spotify.api import SpotifyMusicAPI
from integrations.spotify.utils import get_valid_spotify_token
from music.models import UserMusicService


@sync_to_async
def get_recent_tracks(user):
    service = UserMusicService.objects.filter(
        user=user,
        service="spotify"
    ).first()

    if not service:
        return []

    token = get_valid_spotify_token(service)
    api = SpotifyMusicAPI(token)

    return api.get_recently_played(limit=10)
