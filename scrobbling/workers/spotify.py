import asyncio
import logging

from scrobbling.adapters.spotify import get_recent_tracks
from scrobbling.persistence import save_track_activity, save_track_activity_async

logger = logging.getLogger(__name__)


class SpotifyScrobbleWorker:
    def __init__(self, users, poll_interval: int):
        self.users = users
        self.poll_interval = poll_interval

    async def run(self):
        logger.info(
            f"Spotify worker started users={len(self.users)} "
            f"interval={self.poll_interval}s"
        )

        while True:
            for user in self.users:
                try:
                    await self.scrobble_user(user)
                except Exception:
                    logger.exception(
                        f"Spotify scrobble failed user_id={user.id}"
                    )

            await asyncio.sleep(self.poll_interval)

    async def scrobble_user(self, user):
        tracks = await get_recent_tracks(user)

        for t in tracks:
            await save_track_activity_async(
                user=user,
                track_data={
                    "service": "spotify",
                    "external_id": t["external_id"],
                    "title": t["title"],
                    "artist": t["artist"],
                    "duration_ms": t["duration_ms"],
                    "cover_url": t["cover_url"],
                    "played_at": t["played_at"],
                }
            )

