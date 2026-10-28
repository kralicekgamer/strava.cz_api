import getpass
import json

from strava_cz_api import Strava

username = input("Zadej uzivatelske jmeno: ").strip()
password = getpass.getpass("Zadej heslo: ")
cislo_jidelny = input("Zadej cislo jidelny: ").strip()

with Strava.login(username, password, cislo_jidelny) as strava:
    print("Uzivatel:", strava.username)
    print("Konto:", strava.balance(), "Kč")
    print("Neprectene zpravy:", strava.unread_count())
    print(json.dumps(strava.properties(), indent=2, ensure_ascii=False))
