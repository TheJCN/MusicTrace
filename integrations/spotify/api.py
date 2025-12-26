from typing import List, Optional

import spotipy


class SpotifyMusicAPI:
    """
    Клиент для работы с Spotify Web API.

    Используется ТОЛЬКО после OAuth-авторизации.
    Работает на основе access_token, сохранённого в базе данных.

    Ответственность класса:
    - получение текущего воспроизводимого трека
    - получение последних лайкнутых треков пользователя
    """

    def __init__(self, access_token: str):
        """
        :param access_token: OAuth access token пользователя
        """
        self.sp = spotipy.Spotify(auth=access_token)

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
            "artist": ", ".join(
                artist["name"] for artist in track["artists"]
            ),
            "track_url": track["external_urls"]["spotify"],
            "cover_url": (
                track["album"]["images"][0]["url"]
                if track["album"]["images"]
                else ""
            ),
            "duration_ms": track["duration_ms"],
            "progress_ms": data.get("progress_ms"),
            "is_playing": data.get("is_playing"),
        }

    def get_liked_tracks(self, limit: int = 100) -> List[dict]:
        """
        Получить последние лайкнутые (Saved Tracks) треки пользователя.

        :param limit: максимальное количество треков
        :return: список dict с данными треков
        """
        liked_tracks: List[dict] = []

        offset = 0
        batch_size = 50  # ограничение Spotify API

        while len(liked_tracks) < limit:
            response = self.sp.current_user_saved_tracks(
                limit=batch_size,
                offset=offset
            )

            items = response.get("items", [])
            if not items:
                break

            for item in items:
                track = item.get("track")
                if not track:
                    continue

                liked_tracks.append({
                    "external_id": track["id"],
                    "title": track["name"],
                    "artist": ", ".join(
                        artist["name"] for artist in track["artists"]
                    ),
                    "track_url": track["external_urls"]["spotify"],
                    "cover_url": (
                        track["album"]["images"][0]["url"]
                        if track["album"]["images"]
                        else ""
                    ),
                    "duration_ms": track["duration_ms"],
                })

                if len(liked_tracks) >= limit:
                    break

            offset += batch_size

        return liked_tracks
