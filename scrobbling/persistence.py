from django.utils import timezone
from asgiref.sync import sync_to_async
from music.models import Track, UserTrackActivity


def save_track_activity(*, user, track_data: dict):
    track, _ = Track.objects.get_or_create(
        service=track_data["service"],
        external_id=track_data["external_id"],
        defaults={
            "title": track_data["title"],
            "artist": track_data["artist"],
            "track_url": track_data.get("track_url", ""),
            "cover_url": track_data.get("cover_url", ""),
            "duration_ms": track_data["duration_ms"],
            "genre": track_data.get("genre", ""),
        }
    )

    last_activity = (
        UserTrackActivity.objects
        .filter(user=user, track__service=track.service)
        .select_related("track")
        .order_by("-played_at")
        .first()
    )

    if last_activity and last_activity.track_id == track.id:
        return None

    played_at = track_data.get("played_at") or timezone.now()

    return UserTrackActivity.objects.create(
        user=user,
        track=track,
        played_at=played_at
    )


save_track_activity_async = sync_to_async(
    save_track_activity,
    thread_sensitive=True
)
