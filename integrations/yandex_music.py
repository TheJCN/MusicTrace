import requests
from yandex_music import Client


class YandexMusicAPI:
    def __init__(self, token: str):
        self.token = token
        self.client = Client(token).init()

    def get_current_track(self):
        # 1. Получаем текущий трек через внешний API
        response = requests.get(
            "http://track.mipoh.ru/get_current_track_beta",
            headers={"ya-token": self.token},
            timeout=5
        )

        if response.status_code != 200:            return None

        data = response.json()

        # защита от кривого ответа
        if "track" not in data or "track_id" not in data["track"]:
            return None

        track_id = data["track"]["track_id"]

        # 2. Получаем объект трека через yandex-music
        tracks = self.client.tracks(track_id)
        if not tracks:
            return None

        return tracks[0]
