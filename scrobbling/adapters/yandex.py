from asgiref.sync import sync_to_async
from integrations.yandex.api import YandexMusicAPI
from music.services.yandex_service import save_yandex_current_track


@sync_to_async
def get_current_track_async(token: str):
    api = YandexMusicAPI(token)
    return api.get_current_track()


@sync_to_async
def save_current_track_async(user, yandex_track):
    return save_yandex_current_track(user, yandex_track)