import requests
import json


class StravaApi:
    def __init__(self, sid, cislo_jidelny, cookie, user):
        self.sid = sid
        self.cislo_jidelny = cislo_jidelny
        self.cookie = cookie
        self.user = user


    def call(url, headers, payload):
        response = requests.post(url, headers=headers, json=payload)


        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2, ensure_ascii=False)

        else:
            print(f"Chyba {response.status_code}: {response.text}")


    def getJidelnicekToday(self):
        """Get dnesniho jidelnicku v json formatu"""
        url = "https://app.strava.cz/api/objednavky"

        payload = {
            "cislo": self.cislo_jidelny,
            "sid": self.sid,
            "s5url": "https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "lang": "CZ",
            "konto": 0,
            "podminka": "",
            "ignoreCert": "false"
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        data = json.loads(StravaApi.call(url, headers, payload))

        return data.get("table0", [])


    def getJidelnicekAll(self):
        """Get celeho jidelnicku v json formatu"""
        url = "https://app.strava.cz/api/objednavky"

        payload = {
            "cislo": self.cislo_jidelny,
            "sid": self.sid,
            "s5url": "https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "lang": "CZ",
            "konto": 0,
            "podminka": "",
            "ignoreCert": "false"
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        return StravaApi.call(url, headers, payload)


    def getInfo(self):
        """Ziska info o uzivateli"""
        url = "https://app.strava.cz/api/nactiVlastnostiPA"

        payload = {
            "sid":self.sid,
            "url":"https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "cislo":self.cislo_jidelny,
            "ignoreCert":"false",
            "lang":"CZ",
            "getText":True,
            "checkVersion":True,
            "resetTables":True,
            "frontendFunction":"refreshInformations"
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        return StravaApi.call(url, headers, payload)


    def getJidelna(self):
        """Ziska info o jidelne"""
        url = "https://app.strava.cz/api/jidelnaS5"

        payload = {
            "cislo": self.cislo_jidelny,
            "url":"https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "lang":"CZ",
            "ignoreCert":"false"
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        return StravaApi.call(url, headers, payload)


    def getHistorieKlienta(self, date):
        """
        Ziska info o historii objednavek.
        
        date = počáteční datum měsíce. 
        2025-01-01 - leden
        2025-12-01 - prosinec
        """
        url = "https://app.strava.cz/api/historieKlienta"

        payload = {
            "sid":self.sid,
            "url":"https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "cislo":self.cislo_jidelny,
            "datum": date,
            "lang":"CZ",
            "ignoreCert":"false"
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        return StravaApi.call(url, headers, payload)


    def getPlaby(self):
        """Vrati platby na uctu."""
        url = "https://app.strava.cz/api/platby"

        payload = {
            "sid":self.sid,
            "url":"https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "cislo":self.cislo_jidelny,
            "lang":"CZ",
            "ignoreCert":"false"
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        return StravaApi.call(url, headers, payload)


    def getMessages(self):
        """Vrati zpravy poslane uzivatelovi"""
        url = "https://app.strava.cz/api/messagesGetList"

        payload = {
            "sid":"",
            "idO":"",
            "idJ":self.cislo_jidelny,
            "idU":self.user,
            "typZpravy":""
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        return StravaApi.call(url, headers, payload)


    def postJidlo(self, veta, stav):
        """
        !! NUTNE ZAVOLAT postOrders !! - vice v dokumentaci.
        Prihlasi/odhlasi jidlo
        
        veta = cislo policka/jidla - napr v getJidelnicek()
        stav =  0 ohlasit - 1 prihlasit
        """
        url = "https://app.strava.cz/api/pridejJidloS5"

        payload = {
            "cislo": self.cislo_jidelny,
            "sid": self.sid,
            "url":"https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "veta": veta, 
            "pocet": stav, # 0 ohlasit - 1 prihlasit
            "lang":"CZ",
            "ignoreCert":"false"
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        
        response = requests.post(url, headers=headers, json=payload)


        if response.status_code == 200:
            self.cookie = "; ".join([f"{k}={v}" for k, v in response.cookies.items()])
        
            data = response.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
    
        else:
            print(f"Chyba {response.status_code}: {response.text}")
            return None


    def postOrders(self):
        """Ulozi objednavky"""
        url = "https://app.strava.cz/api/saveOrders"

        payload = {
            "cislo":self.cislo_jidelny,
            "sid":self.sid,
            "url":"https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "xml":None,
            "lang":"CZ",
            "ignoreCert":"false"
        }
        

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        response = requests.post(url, headers=headers, json=payload)


        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2, ensure_ascii=False)

        else:
            print(f"Chyba {response.status_code}: {response.text}")


    def postDen(self, datum, stav):
        """
        !! NUTNE ZAVOLAT postOrders !! - vice v dokumentaci.
        Prihlasi/odhlasi den
        
        datum = datum dne jaky chceme odhlasit. 2025-12-30
        stav =  0 ohlasit - 1 prihlasit
        """

        url = "https://app.strava.cz/api/objednejDenS5"

        payload = {
            "cislo":self.cislo_jidelny,
            "sid":self.sid,
            "url":"https://wss5.strava.cz/WSStravne5_3/WSStravne5.svc",
            "datum":datum,
            "pocet":stav,
            "lang":"CZ",
            "ignoreCert":"false"
        }

        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "Cookie": self.cookie, 
            "Referer": "https://app.strava.cz/"
        }

        
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            self.cookie = "; ".join([f"{k}={v}" for k, v in response.cookies.items()])
        
            data = response.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
    
        else:
            print(f"Chyba {response.status_code}: {response.text}")


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
            return sid

        else:
            print(f"Chyba {response.status_code}: {response.text}")
