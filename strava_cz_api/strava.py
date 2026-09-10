import requests
import json
from .action import Get, Post


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

    def _get(self, url, payload):
        data, self.cookie = Get.call(url, payload, cookie=self.cookie)
        return data

    def _post(self, url, payload):
        data, self.cookie = Post.call(url, payload, cookie=self.cookie)
        return data

    def getJidelnicekToday(self):
        """
        Vrátí dnešní jídelníček.

        :return: list[dict]
        """
        return self.getJidelnicekAll().get("table0", [])

    def getJidelnicekAll(self):
        """
        Vrátí celý jídelníček.

        :return: dict
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

        return self._get(url, payload)

    def getInfo(self):
        """
        Vrátí info o uživateli.

        :return: dict
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
            "resetTables" : False,
            "frontendFunction": "refreshInformations"
        }

        return self._get(url, payload)

    def getUsername(self):
        """
        Vrátí uživatelské jméno.

        :return: str
        """
        return self.getInfo().get("id")

    def getJidelna(self):
        """
        Získá informaci o jídelně.

        :return: dict
        """
        url = f"{self.base}/jidelnaS5"

        payload = {
            "cislo": self.cislo_jidelny,
            "url": self.s5url,
            "lang": self.lang,
            "ignoreCert": "false"
        }

        return self._get(url, payload)

    def getHistorieKlienta(self, date):
        """
        Získá info o historii objednávek.
        
        date = počáteční datum měsíce (např. 2025-01-01).

        :return: dict
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

        return self._get(url, payload)

    def getPlatby(self):
        """
        Vrátí platby na účtu.

        :return: dict
        """
        url = f"{self.base}/platby"

        payload = {
            "sid": self.sid,
            "url": self.s5url,
            "cislo": self.cislo_jidelny,
            "lang": self.lang,
            "ignoreCert": "false"
        }

        return self._get(url, payload)

    def getMessages(self):
        """
        Vrátí zprávy poslané uživatelovi.

        :return: dict
        """
        url = f"{self.base}/messagesGetList"

        payload = {
            "sid": "",
            "idO":"",
            "idJ": self.cislo_jidelny,
            "idU": self.getUsername(),
            "typZpravy": ""
        }

        return self._get(url, payload)

    def getProtokol(self):
        """
        Vrátí protokol.

        :return: dict
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

        return self._get(url, payload)

    def getVydej(self):
        """
        Vrátí list vydaných jídel.

        :return: dict
        """
        url = f"{self.base}/vydej"

        payload = {
            "cislo": self.cislo_jidelny,
            "s5url": self.s5url,
            "sid": self.sid,
            "ignoreCert": "false",
            "lang": self.lang,
        }

        return self._get(url, payload)

    def postJidlo(self, veta, stav):
        """
        Přihlásí nebo odhlásí jídlo.
        
        veta = číslo políčka/jídla - jde získat např. z getJidelnicek()
        stav = 0 odhlásit, 1 přihlásit

        :return: dict
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

        return self._post(url, payload)

    def postOrders(self):
        """
        Uloží objednávky.

        :return: dict
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
        
        return self._post(url, payload)

    def postDen(self, datum, stav):
        """
        Přihlásí nebo odhlásí celý den.
        
        datum = datum dne jaký chceme odhlásit (např. 2025-12-30)
        stav = 0 odhlásit, 1 přihlásit

        :return: dict
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

        return self._post(url, payload)

    def resetChanges(self):
        """
        Resetuje neuložené změny v komunikaci. Může trvat dlouho!

        :return: dict
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
            "resetTables" : True,
            "frontendFunction": "refreshInformations"
        }

        return self._post(url, payload)


class Public:
    @staticmethod
    def getJidelnicek(cislo_jidelny, lang="CZ"):
        """
        Získání veřejného jídelníčku.

        :return: dict
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

        data, _ = Get.call(url, payload)
        return data

    @staticmethod
    def getJidelna(cislo_jidelny):
        """
        Vrátí informaci o jídelně.

        :return: dict
        """
        url = "https://app.strava.cz/api/s4Polozky"

        payload = {
            "cislo": cislo_jidelny,
            "lang": "CZ",
            "polozky": "V_NAZEV,V_ULICE,V_MESTO,V_PSC,V_TELEFON,V_UCET,V_EMAIL,V_URL,DATCAS_AKT,VERZE,URLWSDL_S-URL,GPSDELKA,GPSSIRKA,IGN_CERT,TEXT_ANON,LOGO"
        }

        data, _ = Get.call(url, payload)
        return data

    @staticmethod
    def getVersion(cislo_jidelny):
        """
        Pomocná metoda co vrátí verzi softwaru jídelny.

        :return: str
        """
        verze = Public.getJidelna(cislo_jidelny).get("verze")
        return verze[0] if verze else None

    @staticmethod
    def getS5url(cislo_jidelny):
        """
        Pomocná metoda co vrátí URL jídelny.

        :return: str - s5url jídelny
        """
        urls = Public.getJidelna(cislo_jidelny).get("urlwsdl_s")
        return urls[0] if urls else ""

    @staticmethod
    def getJidelny():
        """
        Vrátí seznam všech jídelen a jejich čísel.

        :return: dict
        """
        url = "https://app.strava.cz/api/zarAMesta"
        
        payload = {
            "lang": "CZ"
        }

        data, _ = Get.call(url, payload)
        return data


class Auth:
    @staticmethod
    def login(username, password, cislo_jidelny, lang="CZ", zustat_prihlasen=True, cookie="NEXT_LOCALE=cs"):
        """
        Přihlásí uživatele a vrátí data a session cookies pro další komunikaci.

        :return: tuple[dict, str]
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

    @staticmethod
    def getCredentials(data):
        """
        Vyfiltruje SID a s5url z funkce login.

        :return: tuple[str, str]
        """
        parsed_data = json.loads(data) if isinstance(data, str) else data
        sid = parsed_data.get("sid")
        s5url = parsed_data.get("s5url")
        return sid, s5url
