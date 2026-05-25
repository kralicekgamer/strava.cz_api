import requests
import json
from action import Get, Post

from action import (
    StravaError,
    JidelnaNenalezenaError,
    ChybneHesloError,
    BackendError,
    ChybneSID
)

__all__ = [
    "Api",
    "Auth",
    "StravaError",
    "JidelnaNenalezenaError",
    "ChybneHesloError",
    "BackendError",
    "ChybneSID"
]


class Api:
    def __init__(self, sid, s5url, cislo_jidelny, cookie="NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D", lang="CZ"):
        if lang not in ("CZ", "EN", "SK"):
            raise ValueError("Podporované jazyky: EN, CZ, SK")
        
        self.sid = sid
        self.lang = lang
        self.cislo_jidelny = cislo_jidelny
        self.cookie = cookie
        self.s5url = s5url

        self.base = "https://app.strava.cz/api"


    def getJidelnicekToday(self):
        """
        Vrátí dnešní jídelníček
        """
        return json.loads(self.getJidelnicekAll()).get("table0", [])


    def getJidelnicekAll(self):
        """
        Vrátí celý jídelníček
        """
        url = f"{self.base}/objednavky"

        payload = {
            "cislo": self.cislo_jidelny,
            "sid": self.sid,
            "s5url": self.s5url,
            "lang": self.lang,
            "konto": 0,
            "podminka": "",
            "ignoreCert": "false"
        }

        return Get.call(url, payload)


    def getInfo(self):
        """
        Vrátí info o uživateli
        """
        url = f"{self.base}/nactiVlastnostiPA"

        payload = {
            "sid": self.sid,
            "url": self.s5url,
            "cislo": self.cislo_jidelny,
            "ignoreCert": "false",
            "lang": self.lang,
            "getText": True,
            "checkVersion": True,
            "resetTables" :True,
            "frontendFunction": "refreshInformations"
        }


        return Get.call(url, payload)
    

    def getUsername(self):
        """
        Vrátí uživatelské jméno
        """

        return json.loads(self.getInfo()).get("id")


    def getJidelna(self):
        """
        Získá informaci o jídělně
        """

        url = f"{self.base}/jidelnaS5"

        payload = {
            "cislo": self.cislo_jidelny,
            "url": self.s5url,
            "lang": self.lang,
            "ignoreCert": "false"
        }


        return Get.call(url, payload)


    def getHistorieKlienta(self, date):
        """
        Získá info o historii objednávek.
        
        date = počáteční datum měsíce. 
        2025-01-01 - leden
        2025-12-01 - prosinec
        """

        url = f"{self.base}/historieKlienta"

        payload = {
            "sid": self.sid,
            "url": self.s5url,
            "cislo": self.cislo_jidelny,
            "datum": date,
            "lang": self.lang,
            "ignoreCert": "false"
        }


        return Get.call(url, payload)


    def getPlaby(self):
        """
        Vrátí platby na účtu.
        """

        url = f"{self.base}/platby"

        payload = {
            "sid": self.sid,
            "url": self.s5url,
            "cislo": self.cislo_jidelny,
            "lang": self.lang,
            "ignoreCert": "false"
        }


        return Get.call(url, payload)


    def getMessages(self):
        """
        Vratí zprávy poslané uživatelovi.
        """

        url = f"{self.base}/messagesGetList"

        payload = {
            "sid": "",
            "idO":"",
            "idJ": self.cislo_jidelny,
            "idU": self.getUsername(),
            "typZpravy": ""
        }

        return Get.call(url, payload)


    def getProtokol(self):
        """
        Vrátí protokol.
        """

        url = f"{self.base}/getProtokol"

        payload = {
            "cislo": self.cislo_jidelny,
            "s5url": self.s5url,
            "sid": self.sid,
            "ignoreCert": "false",
            "lang": self.lang,
            "uroven": "KP",
            "evCislo": 0
        }


        return Get.call(url, payload)

    def getVydej(self):
        """
        Vrátí list vydaných jídel.
        """

        url = f"{self.base}/vydej"

        payload = {
            "cislo": self.cislo_jidelny,
            "s5url": self.s5url,
            "sid": self.sid,
            "ignoreCert": "false",
            "lang": self.lang,
        }


        return Get.call(url, payload)


    def postJidlo(self, veta, stav):
        """
        Příhlásí nebo odhlásí jídlo.
        
        veta = číslo políčka/jídla - jde získat např. z getJidelnicek()
        stav =  0 odhlásit - 1 přihlásit
        """
        url = f"{self.base}/pridejJidloS5"

        payload = {
            "cislo": self.cislo_jidelny,
            "sid": self.sid,
            "url": self.s5url,
            "veta": veta, 
            "pocet": stav, # 0 ohlasit - 1 prihlasit
            "lang": self.lang,
            "ignoreCert": "false"
        }

        self.cookie = Post.call(url, payload, self.cookie)

        return self.cookie


    def postOrders(self):
        """
        Uloží objednávky
        """
        url = f"{self.base}/saveOrders"


        payload = {
            "cislo": self.cislo_jidelny,
            "sid": self.sid,
            "url": self.s5url,
            "xml": None,
            "lang": self.lang,
            "ignoreCert": "false"
        }
        
        self.cookie = Post.call(url, payload, self.cookie)

        return self.cookie


    def postDen(self, datum, stav):
        """
        Přihlásí nebo ohlásí celý den.
        
        datum = datum dne jaký chceme odhlásit. 2025-12-30
        stav =  0 ohlasit - 1 prihlasit
        """

        url = f"{self.base}/objednejDenS5"

        payload = {
            "cislo": self.cislo_jidelny,
            "sid": self.sid,
            "url": self.s5url,
            "datum": datum,
            "pocet": stav,
            "lang": self.lang,
            "ignoreCert": "false"
        }

        self.cookie = Post.call(url, payload, self.cookie)

        return self.cookie


class Public:
    def getJidelnicek(cislo_jidelny, lang):
        """
        Získání public jídelníčků.
        """
        if lang not in ("CZ", "EN", "SK"):
            raise ValueError("Podporované jazyky: EN, CZ, SK")

        url = "https://app.strava.cz/api/jidelnicky"

        payload = {
            "cislo": cislo_jidelny,
            "s5url": Public.getS5url(cislo_jidelny),
            "lang": lang,
            "ignoreCert": False
        }

        return Get.call(url, payload)

    def getJidelna(cislo_jidelny):
        """
        Vrátí informaci o jídelně.
        """
        url = "https://app.strava.cz/api/s4Polozky"

        payload = {
            "cislo": cislo_jidelny,
            "lang": "CZ",
            "polozky": "V_NAZEV,V_ULICE,V_MESTO,V_PSC,V_TELEFON,V_UCET,V_EMAIL,V_URL,DATCAS_AKT,VERZE,URLWSDL_S-URL,GPSDELKA,GPSSIRKA,IGN_CERT,TEXT_ANON,LOGO"}

        return Get.call(url, payload)

    def getS5url(cislo_jidelny):
        """
        Pomocná metoda co vratí url jídelny.
        """
        return json.loads(Public.getJidelna(cislo_jidelny)).get("urlwsdl_s")[0]
        

    def getJidelny():
        """
        Vrátí seznam všech jídelen a jejich čísel.
        """
        url = "https://app.strava.cz/api/zarAMesta"
        
        payload = {
            "lang":"CZ"
        }

        return Get.call(url, payload)


class Auth:
    def login(username, password, cislo_jidelny, lang="CZ", zustat_prihlasen=True, cookie="NEXT_LOCALE=cs"):
        """
        Vrátí data nutná pro další komunikaci.
        """
        if lang not in ("CZ", "EN", "SK"):
            raise ValueError("Podporované jazyky: EN, CZ, SK")
        
        url = "https://app.strava.cz/api/login"

        payload = {
            "cislo": cislo_jidelny,
            "jmeno": username,
            "heslo": password,
            "zustatPrihlasen": zustat_prihlasen,
            "environment": "W",
            "lang": lang
        }

        return Post.call(url, payload, cookie)

    def getCredentials(data):
        """
        Vyfiltruje SID a s5url z funkce login
        """

        sid = data.get("sid")
        s5url = data.get("s5url")
        return sid, s5url
