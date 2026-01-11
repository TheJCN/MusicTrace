from integrations.spotify.api import SpotifyMusicAPI
from integrations.spotify.utils import get_valid_spotify_token
from music.models import Track, UserTrackActivity


def sync_spotify_recent_history(user, service, limit=50):
    access_token = get_valid_spotify_token(service)
    api = SpotifyMusicAPI(access_token)

    tracks = api.get_recently_played(limit=limit)

    for data in tracks:
        track, _ = Track.objects.get_or_create(
            service="spotify",
            external_id=data["external_id"],
            defaults={
                "title": data["title"],
                "artist": data["artist"],
                "track_url": data["track_url"],
                "cover_url": data["cover_url"],
                "duration_ms": data["duration_ms"],
                "genre": "",
            }
        )

        UserTrackActivity.objects.get_or_create(
            user=user,
            track=track,
            played_at=data["played_at"]
        )