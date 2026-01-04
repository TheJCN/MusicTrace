from django.utils import timezone
from music.models import Track, UserTrackActivity


def save_spotify_current_track(user, data: dict):
    """
    Сохраняет текущий трек Spotify и активность пользователя.
    """
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

    last_activity = (
        UserTrackActivity.objects
        .filter(user=user)
        .order_by("-played_at")
        .first()
    )

    if not last_activity or last_activity.track != track:
        UserTrackActivity.objects.create(
            user=user,
            track=track,
            played_at=timezone.now()
        )

    return track
