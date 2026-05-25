import requests
import json


class Get:
    @staticmethod
    def call(url, payload, headers=
        {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D",
            "Referer": "https://app.strava.cz/"
        }):

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise ConnectionError(f"Error: {response.status_code}: {response.text}")

            
        data = response.json()
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

        if response.status_code != 200:
            raise ConnectionError(f"Error: {response.status_code}: {response.text}")

        new_cookie = "; ".join([f"{k}={v}" for k, v in response.cookies.items()])

        return new_cookie



