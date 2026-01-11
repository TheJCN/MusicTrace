import asyncio
import logging
import random

from asgiref.sync import sync_to_async

from music.models import UserMusicService
from scrobbling.adapters.yandex import get_current_track
from scrobbling.persistence import save_track_activity_async

logger = logging.getLogger(__name__)


@sync_to_async
def get_yandex_token(user):
    service = UserMusicService.objects.filter(
        user=user,
        service="yandex"
    ).first()
    return service.access_token if service else None


class YandexScrobbleWorker:
    def __init__(self, users, poll_interval: int):
        self.users = users
        self.poll_interval = poll_interval

    async def run(self):
        logger.info(
            f"Yandex worker started users={len(self.users)} "
            f"interval={self.poll_interval}s"
        )

        while True:
            for user in self.users:
                try:
                    await self.scrobble_user(user)
                except Exception:
                    logger.exception(
                        f"Yandex scrobble failed user_id={user.id}"
                    )

            await asyncio.sleep(
                self.poll_interval + random.uniform(-2, 2)
            )

    async def scrobble_user(self, user):
        token = await get_yandex_token(user)
        if not token:
            return

        track = await get_current_track(token)
        if not track:
            return

        track_data = {
            "service": "yandex",
            "external_id": str(track.id),
            "title": track.title,
            "artist": (
                track.artists[0].name
                if track.artists else "Unknown"
            ),
            "duration_ms": track.duration_ms,
            "cover_url": (
                "https://" + str(track.cover_uri).replace("%%", "orig")
                if track.cover_uri else ""
            ),
        }

        await save_track_activity_async(user=user, track_data=track_data)
