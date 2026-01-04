from abc import ABC, abstractmethod


class BaseLyricsClient(ABC):
    """
    Абстрактный клиент получения текстов песен.
    """

    @abstractmethod
    def get_lyrics(self, artist: str, title: str) -> str | None:
        """
        Возвращает текст песни или None, если не найден.
        """
        raise NotImplementedError