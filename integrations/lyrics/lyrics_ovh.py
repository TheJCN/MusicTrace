import requests
from urllib.parse import quote

from integrations.lyrics.base import BaseLyricsClient


class LyricsOvhClient(BaseLyricsClient):
    BASE_URL = "https://api.lyrics.ovh/v1"

    def get_lyrics(self, artist: str, title: str) -> str | None:
        url = f"{self.BASE_URL}/{quote(artist)}/{quote(title)}"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            return None

        data = response.json()
        return data.get("lyrics")