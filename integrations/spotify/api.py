from typing import List, Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyMusicAPI:
    """
    Сервис для работы с Spotify API.

    Предоставляет методы для:
    - получения текущего воспроизводимого трека
    - получения последних лайкнутых треков пользователя

    Использует OAuth2 (Authorization Code Flow).
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        """
        Если access_token / refresh_token переданы — используется сохранённая сессия.
        Иначе запускается стандартный OAuth2 flow.

        Токены рекомендуется хранить в UserMusicService.
        """

        self.auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=(
                "user-read-currently-playing "
                "user-read-playback-state "
                "user-library-read"
            ),
        )

        if access_token:
            self.auth_manager.token_info = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": 3600,
            }

        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_current_track(self) -> Optional[dict]:
        """
        Получить трек, который воспроизводится в данный момент.

        :return: dict с данными трека или None
        """
        data = self.sp.current_user_playing_track()

        if not data or not data.get("item"):
            return None

        track = data["item"]

        return {
            "external_id": track["id"],
            "title": track["name"],
            "artist": ", ".join(artist["name"] for artist in track["artists"]),
            "track_url": track["external_urls"]["spotify"],
            "cover_url": track["album"]["images"][0]["url"]
            if track["album"]["images"]
            else None,
            "duration_ms": track["duration_ms"],
            "is_playing": data.get("is_playing"),
            "progress_ms": data.get("progress_ms"),
        }

    def get_liked_tracks(self, limit: int = 100) -> List[dict]:
        """
        Получить последние лайкнутые треки пользователя.

        В Spotify лайки = 'Saved Tracks'.

        :param limit: количество треков (макс 100 за запрос)
        :return: список dict с данными треков
        """
        liked_tracks: List[dict] = []

        offset = 0
        batch_size = 50  # Spotify API ограничение

        while len(liked_tracks) < limit:
            response = self.sp.current_user_saved_tracks(
                limit=batch_size,
                offset=offset
            )

            items = response.get("items", [])
            if not items:
                break

            for item in items:
                track = item["track"]
                if not track:
                    continue

                liked_tracks.append({
                    "external_id": track["id"],
                    "title": track["name"],
                    "artist": ", ".join(
                        artist["name"] for artist in track["artists"]
                    ),
                    "track_url": track["external_urls"]["spotify"],
                    "cover_url": track["album"]["images"][0]["url"]
                    if track["album"]["images"]
                    else None,
                    "duration_ms": track["duration_ms"],
                })

                if len(liked_tracks) >= limit:
                    break

            offset += batch_size

        return liked_tracks