from asgiref.sync import sync_to_async
from integrations.yandex.api import YandexMusicAPI


@sync_to_async
def get_current_track(token: str):
    api = YandexMusicAPI(token)
    return api.get_current_track()
