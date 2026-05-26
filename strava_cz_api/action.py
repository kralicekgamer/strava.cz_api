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

def raise_api_error(data):
    if data.get("state") != "error":
        return

    number = data.get("number")
    message = data.get("message", "Neznámá chyba")

    exc = ERROR_MAP.get(number, StravaError)
    raise exc(message)


ERROR_MAP = {
    6: JidelnaNenalezenaError,
    15: ChybneSID,
    13405: ChybneHesloError,
    3002: BackendError,
}

class Get:
    @staticmethod
    def call(url, payload, headers=
        {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D",
            "Referer": "https://app.strava.cz/"
        }):

        response = requests.post(url, headers=headers, json=payload)
            
        data = response.json()

        raise_api_error(data)

        return json.dumps(data, indent=2, ensure_ascii=False)
            


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

        new_cookie = "; ".join([f"{k}={v}" for k, v in response.cookies.items()])

        return new_cookie, data


class ResetChanges:
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

        new_cookie = response.cookies.get_dict()

        return new_cookie
