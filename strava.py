import requests
import json
from action import Get, Post

class Api:
    def __init__(self, sid, s5url, cislo_jidelny, cookie="NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D"):
        if len(sid) == 32:
            self.sid = sid

        else:
            raise ValueError("Číslo musí být dlouhé 32 znaků")
        
        self.cislo_jidelny = cislo_jidelny
        self.cookie = cookie
        self.s5url = s5url

        self.base = "https://app.strava.cz/api"


    def getJidelnicekToday(self):
        """
        Vrátí dnešní jídelníček
        """
        return json.loads(Api.getJidelnicekAll()).get("table0", [])


    def getJidelnicekAll(self):
        """
        Vrátí celý jídelníček
        """
        url = f"{self.base}/objednavky"

        payload = {
            "cislo": self.cislo_jidelny,
            "sid": self.sid,
            "s5url": self.s5url,
            "lang": "CZ",
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
            "lang": "CZ",
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
            "lang": "CZ",
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
            "lang": "CZ",
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
            "lang": "CZ",
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
            "lang": "CZ",
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
            "lang": "CZ",
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
            "lang": "CZ",
            "ignoreCert": "false"
        }

        self.cookie = Post.call(url, payload, self.cookie)

        return self.cookie


class Public:
    def getJidelnicek(cislo_jidelny):
        """
        Získání public jídelníčků.
        """
        url = "https://app.strava.cz/api/jidelnicky"

        payload = {
            "cislo":cislo_jidelny,
            "s5url":"https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "lang":"CZ","ignoreCert":False
        }

        return Get.call(url, payload)


class Sid:
    def __init__(self, username, password, cislo_jidelny):
        self.__username = username
        self.__password = password
        self.__cislo_jidelny = cislo_jidelny

    
    def getSid(self):
        url = "https://app.strava.cz/api/login"

        payload = {
            "cislo":self.__cislo_jidelny,
            "jmeno":self.__username,
            "heslo":self.__password,
            "zustatPrihlasen":True,
            "environment":"W",
            "lang":"CZ"
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": "NEXT_LOCALE=cs", 
            "Referer": "https://app.strava.cz/"
        }


        response = requests.post(url, headers=headers, json=payload)


        if response.status_code == 200:
            data = response.json()
            sid = data.get("sid")
            s5url = data.get("s5url")
            return sid, s5url

        else:
            print(f"Chyba {response.status_code}: {response.text}")
