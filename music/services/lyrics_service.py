from django.db import transaction
from django.utils import timezone

from music.models import Track, TrackLyrics, TrackLyricsStats
from integrations.lyrics.lyrics_ovh import LyricsOvhClient


class LyricsService:
    """
    Сервис получения и сохранения текстов песен.

    Правила:
    - текст сохраняется только после N просмотров
    - используется цепочка провайдеров
    """

    SAVE_THRESHOLD = 3

    def __init__(self):
        self.providers = [
            LyricsOvhClient(),
        ]

    def get_lyrics(self, track: Track) -> str | None:
        stored = getattr(track, "lyrics", None)
        if stored:
            self._inc_views(track)
            return stored.lyrics

        lyrics = self._fetch_external(track.artist, track.title)
        if not lyrics:
            return None

        stats = self._inc_views(track)

        if stats.views >= self.SAVE_THRESHOLD:
            TrackLyrics.objects.get_or_create(
                track=track,
                defaults={
                    "lyrics": lyrics,
                    "provider": "musixmatch",
                }
            )

        return lyrics

    def _fetch_external(self, artist: str, title: str) -> str | None:
        for provider in self.providers:
            lyrics = provider.get_lyrics(artist, title)
            if lyrics:
                return lyrics
        return None

    @transaction.atomic
    def _inc_views(self, track: Track) -> TrackLyricsStats:
        stats, _ = TrackLyricsStats.objects.select_for_update().get_or_create(
            track=track
        )
        stats.views += 1
        stats.last_viewed_at = timezone.now()
        stats.save(update_fields=["views", "last_viewed_at"])
        return stats