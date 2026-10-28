"""
Zpětná kompatibilita s 2.x. Všechny staré metody fungují, ale vypíšou
`DeprecationWarning` s názvem nové metody.
"""
import json
import warnings
from functools import wraps

from ._http import Transport, check_lang
from .client import Strava
from .public import Public as _Public
from .public import canteen_number

LEGACY_COOKIE = "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D"


def _deprecated(new_name):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{function.__qualname__}() je zastaralé, použij {new_name}",
                DeprecationWarning,
                stacklevel=2,
            )
            return function(*args, **kwargs)
        return wrapper
    return decorator


class Api(Strava):
    """Klient z verze 2.x. Nově používej `Strava`."""

    def __init__(self, sid, s5url, cislo_jidelny, cookie=LEGACY_COOKIE, lang="CZ"):
        super().__init__(sid=sid, canteen=cislo_jidelny, s5url=s5url, lang=lang)
        self.transport.seed_cookie(cookie)

    @property
    def cislo_jidelny(self):
        return self.canteen_number

    @property
    def cookie(self):
        return self.transport.cookie_string()

    @_deprecated("Strava.menu_today()")
    def getJidelnicekToday(self):
        return self.menu().get("table0", [])

    @_deprecated("Strava.menu()")
    def getJidelnicekAll(self):
        return self.menu()

    @_deprecated("Strava.user_info()")
    def userInfo(self):
        return self.user_info()

    @_deprecated("Strava.properties()")
    def getInfo(self, resetTables=False):
        return self.properties(reset_tables=resetTables)

    @_deprecated("Strava.username")
    def getUsername(self):
        return self.username

    @_deprecated("Strava.canteen()")
    def getJidelna(self):
        return self.canteen()

    @_deprecated("Strava.history()")
    def getHistorieKlienta(self, date):
        return self.history(date)

    @_deprecated("Strava.payments()")
    def getPlatby(self):
        return self.payments()

    @_deprecated("Strava.messages()")
    def getMessages(self):
        return self.messages()

    @_deprecated("Strava.protocol()")
    def getProtokol(self):
        return self.protocol()

    @_deprecated("Strava.issued_meals()")
    def getVydej(self):
        return self.issued_meals()

    @_deprecated("Strava.order() / Strava.cancel()")
    def postJidlo(self, veta, stav):
        return self.set_meal_count(veta, stav)

    @_deprecated("Strava.save_orders()")
    def postOrders(self):
        return self.save_orders()

    @_deprecated("Strava.order_day() / Strava.cancel_day()")
    def postDen(self, datum, stav):
        return self.set_day(datum, stav)

    @_deprecated("Strava.discard_changes()")
    def resetChanges(self):
        return self.properties(reset_tables=True)

    @_deprecated("Strava.logout()")
    def logOut(self):
        return self.logout()


class Auth:
    """Přihlášení z verze 2.x. Nově používej `Strava.login()`."""

    @staticmethod
    @_deprecated("Strava.login()")
    def login(username, password, cislo_jidelny, lang="CZ", zustat_prihlasen=True, cookie="NEXT_LOCALE=cs"):
        transport = Transport()
        transport.seed_cookie(cookie)
        data = Strava._login_request(
            transport, username, password, canteen_number(cislo_jidelny), check_lang(lang), zustat_prihlasen
        )
        return data, transport.cookie_string()

    @staticmethod
    def getCredentials(data):
        parsed = json.loads(data) if isinstance(data, str) else data
        return parsed.get("sid"), parsed.get("s5url")


class Public(_Public):
    """`Public` rozšířený o staré názvy metod z 2.x."""

    @staticmethod
    @_deprecated("Public.menu()")
    def getJidelnicek(cislo_jidelny, lang="CZ"):
        return _Public.menu(cislo_jidelny, lang)

    @staticmethod
    @_deprecated("Public.canteen()")
    def getJidelna(cislo_jidelny):
        return _Public.canteen(cislo_jidelny)

    @staticmethod
    @_deprecated("Public.version()")
    def getVersion(cislo_jidelny):
        return _Public.version(cislo_jidelny)

    @staticmethod
    @_deprecated("Public.s5url()")
    def getS5url(cislo_jidelny):
        return _Public.s5url(cislo_jidelny)

    @staticmethod
    @_deprecated("Public.canteens()")
    def getJidelny():
        return _Public.canteens()
