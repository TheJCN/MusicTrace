import asyncio
import logging

from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

from .manager import calculate_workers, calculate_poll_interval
from .workers import YandexScrobbleWorker

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
        logger.error('No users found')
        return

    workers_count = calculate_workers(len(users))
    poll_interval = calculate_poll_interval(len(users), workers_count)

    logger.info(
        f'Starting scrobbling: '
        f'users={len(users)} '
        f'workers={workers_count} '
        f'interval={poll_interval}s'
    )

    user_chunks = list(chunk_users(users, workers_count))

    tasks = [
        YandexScrobbleWorker(chunk, poll_interval).run()
        for chunk in user_chunks
    ]

    await asyncio.gather(*tasks)