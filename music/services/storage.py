from music.models import Track, UserTrackActivity


def save_track_and_activity(user, yandex_track):
    artist = (
        yandex_track.artists[0].name
        if yandex_track.artists else "Unknown"
    )

    genre = ""
    if yandex_track.albums and yandex_track.albums[0].genre:
        genre = yandex_track.albums[0].genre

    track, created = Track.objects.get_or_create(
        external_id=str(yandex_track.id),
        defaults={
            "title": yandex_track.title,
            "artist": artist,
            "duration_ms": yandex_track.duration_ms,
            "genre": genre,
        }
    )

    print("Track title:", yandex_track.title)
    print("Artist:", artist)
    print("Genre:", genre)
    print("Track duration (ms):", yandex_track.duration_ms)

    if not created:
        track.title = yandex_track.title
        track.artist = artist
        track.duration_ms = yandex_track.duration_ms
        track.genre = genre
        track.save()

    UserTrackActivity.objects.create(
        user=user,
        track=track
    )

    return track