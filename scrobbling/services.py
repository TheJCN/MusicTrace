from django.utils import timezone
from asgiref.sync import sync_to_async

from music.models import Track, UserTrackActivity


def save_track_activity(*, user, track_data: dict):
    track, _ = Track.objects.get_or_create(
        service=track_data['service'],
        external_id=track_data['external_id'],
        defaults={
            'title': track_data['title'],
            'artist': track_data['artist'],
            'track_url': track_data.get('track_url', ''),
            'cover_url': track_data.get('cover_url', ''),
            'duration_ms': track_data['duration_ms'],
            'genre': track_data.get('genre', ''),
        }
    )

    played_at = track_data.get('played_at') or timezone.now()

    exists = UserTrackActivity.objects.filter(
        user=user,
        track=track,
        played_at=played_at
    ).exists()

    if exists:
        return None

    return UserTrackActivity.objects.create(
        user=user,
        track=track,
        played_at=played_at
    )


@sync_to_async
def save_track_activity_async(*, user, track_data):
    return save_track_activity(user=user, track_data=track_data)