"""Uloží objednané obědy do kalendáře (soubor .ics jde importovat do Google/Outlook kalendáře)."""
import getpass

from strava_cz_api import Strava

username = input("Uživatelské jméno: ")
password = getpass.getpass("Heslo: ")
jidelna = input("Číslo jídelny: ")

with Strava.login(username, password, jidelna) as strava:
    strava.export_ics("obedy.ics")
    print("Uloženo do obedy.ics")
