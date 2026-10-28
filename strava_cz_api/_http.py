import json

import requests

from .errors import ApiError, StravaConnectionError, raise_api_error

BASE_URL = "https://app.strava.cz/api"
DEFAULT_TIMEOUT = 30
LANGS = ("CZ", "EN", "SK")

DEFAULT_HEADERS = {
    "Content-Type": "text/plain;charset=UTF-8",
    "Referer": "https://app.strava.cz/",
    "Origin": "https://app.strava.cz",
    "User-Agent": "strava-cz-api/3.0 (python-requests)",
}


def check_lang(lang):
    lang = (lang or "CZ").upper()
    if lang not in LANGS:
        raise ValueError("Podporované jazyky: EN, CZ, SK")
    return lang


class Transport:
    """
    Sdílené HTTP spojení na app.strava.cz.

    Všechny endpointy Stravy se volají jako POST s JSON tělem (stejně jako
    to dělá webová aplikace). Cookies drží `requests.Session`.
    """

    def __init__(self, timeout=DEFAULT_TIMEOUT, session=None, base_url=BASE_URL):
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.session.cookies.set("NEXT_LOCALE", "cs", domain="app.strava.cz")

    def seed_cookie(self, cookie):
        """Nahraje cookies ze stringu `a=1; b=2` (kompatibilita s 2.x)."""
        for part in (cookie or "").split(";"):
            if "=" in part:
                key, value = part.strip().split("=", 1)
                self.session.cookies.set(key.strip(), value.strip(), domain="app.strava.cz")

    def cookie_string(self):
        return "; ".join(f"{c.name}={c.value}" for c in self.session.cookies)

    def post(self, endpoint, payload):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.post(url, data=json.dumps(payload), timeout=self.timeout)
        except requests.RequestException as error:
            raise StravaConnectionError(f"Nepodařilo se spojit se Stravou ({endpoint}): {error}") from error

        try:
            data = response.json()
        except ValueError:
            raise ApiError(
                f"Strava vrátila neplatnou odpověď (HTTP {response.status_code}) z {endpoint}: {response.text[:200]}",
                number=response.status_code,
            ) from None

        raise_api_error(data)
        return data

    def close(self):
        self.session.close()


_shared = None


def shared_transport():
    """Transport pro veřejné endpointy (bez přihlášení), vytvořený líně."""
    global _shared
    if _shared is None:
        _shared = Transport()
    return _shared
