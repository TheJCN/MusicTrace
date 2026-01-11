from django.utils import timezone
from music.models import UserTrackActivity, Track


def save_yandex_current_track(user, yandex_track):
    """
    Сохраняет текущий трек Яндекс Музыки и активность пользователя.
    """

    artist = (
        yandex_track.artists[0].name
        if yandex_track.artists else "Unknown"
    )

    genre = ""
    if yandex_track.albums and yandex_track.albums[0].genre:
        genre = yandex_track.albums[0].genre

    cover_url = ""
    if yandex_track.cover_uri:
        cover_url = "https://" + str(yandex_track.cover_uri).replace("%%", "orig")

    track, _ = Track.objects.get_or_create(
        service="yandex",
        external_id=str(yandex_track.id),
        defaults={
            "title": yandex_track.title,
            "artist": artist,
            "track_url": "",
            "cover_url": cover_url,
            "duration_ms": yandex_track.duration_ms,
            "genre": genre,
        }
    )

    last_activity = (
        UserTrackActivity.objects
        .filter(user=user)
        .order_by("-played_at")
        .first()
    )

    now = timezone.now()

    if not last_activity or last_activity.track != track:
        UserTrackActivity.objects.create(
            user=user,
            track=track,
            played_at=now
        )

    return track
