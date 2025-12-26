import requests
from typing import List, Optional

from yandex_music import Client
from yandex_music.track import track as YandexTrack


class YandexMusicAPI:
    """
    Сервис для работы с Яндекс Музыкой.

    Предоставляет методы для:
    - получения текущего воспроизводимого трека
    - получения последних лайкнутых треков пользователя

    Класс инкапсулирует работу с yandex-music SDK и внешними API.
    """

    def __init__(self, token: str):
        self.token = token
        self.client = Client(token).init()

    def get_current_track(self) -> Optional[YandexTrack]:
        """
        Получить трек, который воспроизводится в данный момент.

        Используется сторонний API, так как официальный SDK
        не предоставляет надёжного метода real-time трека.

        :return: объект yandex_music.track.Track или None
        """
        response = requests.get(
            "http://track.mipoh.ru/get_current_track_beta",
            headers={"ya-token": self.token},
            timeout=5
        )

        if response.status_code != 200:
            return None

        data = response.json()

        track_id = data.get("track", {}).get("track_id")
        if not track_id:
            return None

        tracks = self.client.tracks(track_id)
        if not tracks:
            return None

        return tracks[0]

    def get_liked_tracks(self, limit: int = 100) -> List[YandexTrack]:
        """
        Получить последние лайкнутые треки пользователя.

        В Яндекс Музыке лайкнутые треки хранятся в плейлисте
        «Мне нравится», доступном через users_likes_tracks().

        :param limit: максимальное количество треков
        :return: список объектов yandex_music.track.Track
        """
        liked_tracks: List[YandexTrack] = []

        for like in self.client.users_likes_tracks():
            if like.track:
                liked_tracks.append(like.track)

            if len(liked_tracks) >= limit:
                break

        return liked_tracks