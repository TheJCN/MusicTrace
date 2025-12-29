import asyncio
import random
import logging

from asgiref.sync import sync_to_async
from music.models import UserMusicService
from scrobbling.adapters.yandex import (
    get_current_track_async,
    save_current_track_async,
)

logger = logging.getLogger(__name__)


@sync_to_async
def get_yandex_token(user):
    service = UserMusicService.objects.filter(
        user=user,
        service='yandex'
    ).first()
    return service.access_token if service else None


class YandexScrobbleWorker:
    def __init__(self, users, poll_interval: int):
        self.users = users
        self.poll_interval = poll_interval

    async def run(self):
        logger.info(
            f'Scrobbling worker started '
            f'users={len(self.users)} '
            f'interval={self.poll_interval}s'
        )

        while True:
            for user in self.users:
                try:
                    await self.scrobble_user(user)
                except Exception:
                    logger.exception(
                        f'Scrobbling failed user_id={user.id}'
                    )

            await asyncio.sleep(
                self.poll_interval + random.uniform(-2, 2)
            )

    async def scrobble_user(self, user):
        token = await get_yandex_token(user)
        if not token:
            return

        logger.debug(f'Start scrobbling user_id={user.id}')

        yandex_track = await get_current_track_async(token)

        if not yandex_track:
            logger.debug(f'No current track user_id={user.id}')
            return

        track = await save_current_track_async(user, yandex_track)

        logger.info(
            f'Scrobbled user_id={user.id} '
            f'{track.artist} — {track.title}'
        )