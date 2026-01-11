import asyncio
import logging

from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

from scrobbling.manager import (
    calculate_workers,
    calculate_poll_interval,
    SPOTIFY_INTERVAL,
    USERS_REFRESH_INTERVAL,
)
from scrobbling.workers.yandex import YandexScrobbleWorker
from scrobbling.workers.spotify import SpotifyScrobbleWorker

logger = logging.getLogger(__name__)


@sync_to_async
def get_users():
    return list(User.objects.all())


def chunk_users(users, chunks_count):
    size = max(1, len(users) // chunks_count)
    for i in range(0, len(users), size):
        yield users[i:i + size]


async def start_scrobbling():
    current_user_ids: set[int] = set()
    tasks: list[asyncio.Task] = []

    while True:
        users = await get_users()
        user_ids = {u.id for u in users}

        if user_ids != current_user_ids:
            logger.info(
                f"Users changed: {len(current_user_ids)} → {len(user_ids)}. "
                f"Restarting scrobbling workers."
            )

            for task in tasks:
                task.cancel()
            tasks.clear()

            if users:
                workers_count = calculate_workers(len(users))

                yandex_interval = calculate_poll_interval(
                    len(users),
                    workers_count
                )
                spotify_interval = SPOTIFY_INTERVAL

                user_chunks = list(
                    chunk_users(users, workers_count)
                )

                for chunk in user_chunks:
                    tasks.append(
                        asyncio.create_task(
                            YandexScrobbleWorker(
                                chunk,
                                yandex_interval
                            ).run()
                        )
                    )
                    tasks.append(
                        asyncio.create_task(
                            SpotifyScrobbleWorker(
                                chunk,
                                spotify_interval
                            ).run()
                        )
                    )

            current_user_ids = user_ids

        await asyncio.sleep(USERS_REFRESH_INTERVAL)
