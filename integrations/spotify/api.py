from typing import Optional

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

    def get_recently_played(self, limit: int = 50) -> list[dict]:
        response = self.sp.current_user_recently_played(limit=limit)

        tracks = []
        for item in response.get("items", []):
            track = item.get("track")
            if not track:
                continue

            tracks.append({
                "external_id": track["id"],
                "title": track["name"],
                "artist": ", ".join(a["name"] for a in track["artists"]),
                "track_url": track["external_urls"]["spotify"],
                "cover_url": (
                    track["album"]["images"][0]["url"]
                    if track["album"]["images"] else ""
                ),
                "duration_ms": track["duration_ms"],
                "played_at": item.get("played_at"),
            })

        return tracks
