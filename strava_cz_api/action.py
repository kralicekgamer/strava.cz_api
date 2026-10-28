"""Zpětná kompatibilita s 2.x – chyby se nově importují z `strava_cz_api` nebo `strava_cz_api.errors`."""
from ._http import Transport
from .errors import *  # noqa: F401,F403
from .errors import ERROR_MAP, raise_api_error  # noqa: F401


def merge_cookies(old_cookie, response_cookies):
    cookies = {}
    for part in (old_cookie or "").split(";"):
        if "=" in part:
            key, value = part.strip().split("=", 1)
            cookies[key.strip()] = value.strip()
    cookies.update(dict(response_cookies or {}))
    return "; ".join(f"{key}={value}" for key, value in cookies.items())


class Post:
    @staticmethod
    def call(url, payload, cookie=None, headers=None):
        transport = Transport(base_url=url.rsplit("/", 1)[0])
        transport.seed_cookie(cookie)
        if headers:
            transport.session.headers.update(headers)
        data = transport.post(url.rsplit("/", 1)[1], payload)
        return data, transport.cookie_string()


Get = Post
