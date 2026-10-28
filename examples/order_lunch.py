"""Přihlásí na zadaný den první objednatelný oběd."""
import getpass
from datetime import date, timedelta

from strava_cz_api import Strava

username = input("Uživatelské jméno: ")
password = getpass.getpass("Heslo: ")
jidelna = input("Číslo jídelny: ")
den = input("Den (YYYY-MM-DD) [zítra]: ").strip() or (date.today() + timedelta(days=1)).isoformat()

with Strava.login(username, password, jidelna) as strava:
    jidla = strava.menu_for(den)
    if any(meal.ordered for meal in jidla):
        print("Na tento den už máš objednáno.")
        raise SystemExit

    volne = [meal for meal in jidla if meal.can_order]
    if not volne:
        print("Na tento den nejde nic objednat.")
        raise SystemExit

    jidlo = volne[0]
    strava.order(jidlo)
    strava.save_orders()  # bez uložení se objednávka neprojeví
    print(f"Objednáno: {jidlo.name} ({jidlo.price} Kč)")
