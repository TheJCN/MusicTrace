import asyncio
import logging

from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

from scrobbling.manager import (
    calculate_workers,
    calculate_poll_interval,
    SPOTIFY_INTERVAL,
)
from scrobbling.workers.yandex import YandexScrobbleWorker
from scrobbling.workers.spotify import SpotifyScrobbleWorker

logger = logging.getLogger(__name__)


def chunk_users(users, chunks_count):
    size = max(1, len(users) // chunks_count)
    for i in range(0, len(users), size):
        yield users[i:i + size]


@sync_to_async
def get_users():
    return list(User.objects.all())


async def start_scrobbling():
    users = await get_users()
    if not users:
        logger.warning("No users found for scrobbling")
        return

    workers_count = calculate_workers(len(users))

    yandex_interval = calculate_poll_interval(
        len(users),
        workers_count
    )

    spotify_interval = SPOTIFY_INTERVAL

    logger.info(
        f"Scrobbling config: "
        f"yandex_interval={yandex_interval}s "
        f"spotify_interval={spotify_interval}s "
        f"workers={workers_count}"
    )

    user_chunks = list(chunk_users(users, workers_count))
    tasks = []

    for chunk in user_chunks:
        tasks.append(
            YandexScrobbleWorker(chunk, yandex_interval).run()
        )
        tasks.append(
            SpotifyScrobbleWorker(chunk, spotify_interval).run()
        )

    await asyncio.gather(*tasks)

