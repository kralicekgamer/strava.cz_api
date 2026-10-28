# made by OpiKula
import getpass

from strava_cz_api import Strava, StravaError

username = input("Zadej zde svoje uživatelské jméno: ")
password = getpass.getpass("Zadej zde svoje heslo: ")
jidelna = input("Zadej zde číslo jídelny: ")

try:
    strava = Strava.login(username, password, jidelna)
except StravaError as error:
    print("Přihlášení selhalo:", error.message)
    raise SystemExit(1)

# `with` se na konci sám odhlásí
with strava:
    for meal in strava.menu_today():
        stav = "objednáno" if meal.ordered else "neobjednáno"
        print(f"{meal.meal_type}: {meal.name} ({stav})")
