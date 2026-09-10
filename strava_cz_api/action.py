import requests
import json

class StravaError(Exception):
    pass

class JidelnaNenalezenaError(StravaError):
    pass

class ChybneHesloError(StravaError):
    pass

class BackendError(StravaError):
    pass

class ChybneSID(StravaError):
    pass

class ChybnyUzivatel(StravaError):
    pass

class NelzePrihlasit(StravaError):
    pass

class NelzeVytvoritSID(StravaError):
    pass

class AuthError(StravaError):
    pass

class S5Payload(StravaError):
    pass

class S5AndJidelnaPayload(StravaError):
    pass

class ApiError(StravaError):
    pass

def raise_api_error(data):
    if not isinstance(data, dict):
        return
    
    if data.get("state") != "error":
        return

    number = data.get("number")
    message = data.get("message", "Neznámá chyba")

    exc = ERROR_MAP.get(number, StravaError)
    error_msg = f"""

---=== Error: #{number} ===---
{message}
    """
    raise exc(error_msg)


ERROR_MAP = {
    6: JidelnaNenalezenaError,
    14: NelzeVytvoritSID,
    15: ChybneSID,
    30: S5AndJidelnaPayload,
    35: NelzePrihlasit,
    3002: BackendError,
    10102: AuthError,
    13201: S5Payload,
    13404: ChybnyUzivatel,
    13405: ChybneHesloError,
    "99+": ApiError,
}

def merge_cookies(old_cookie, response_cookies):
    cookies = {}
    if old_cookie:
        for part in old_cookie.split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                cookies[k.strip()] = v.strip()
    if response_cookies:
        for k, v in response_cookies.items():
            cookies[k] = v
    return "; ".join([f"{k}={v}" for k, v in cookies.items()])


class Get:
    @staticmethod
    def call(url, payload, cookie=None, headers=None):
        if headers is None:
            headers = {
                "Content-Type": "text/plain;charset=UTF-8",
                "Referer": "https://app.strava.cz/"
            }
            if cookie:
                headers["Cookie"] = cookie
            else:
                headers["Cookie"] = "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D"

        response = requests.get(url, headers=headers, json=payload)
            
        data = response.json()

        raise_api_error(data)

        new_cookie = merge_cookies(headers.get("Cookie", ""), response.cookies)

        return data, new_cookie


class Post:
    @staticmethod
    def call(url, payload, cookie, headers=None):
        if headers is None:
            headers = {
                "Content-Type": "text/plain;charset=UTF-8",
                "Cookie": cookie,
                "Referer": "https://app.strava.cz/"
            }

        response = requests.post(url, headers=headers, json=payload)

        data = response.json()

        raise_api_error(data)

        new_cookie = merge_cookies(headers.get("Cookie", ""), response.cookies)

        return data, new_cookie
