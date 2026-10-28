"""
Živý test endpointů proti app.strava.cz.

    python test_api.py           # jen čtecí endpointy
    python test_api.py --write   # navíc endpointy, které mění objednávky (změny se na konci zahodí)
"""
import getpass
import sys

from strava_cz_api import Public, Strava

WRITE = "--write" in sys.argv

passed = 0
failed = 0


def run(name, function):
    global passed, failed
    try:
        function()
        print(f"PASS  {name}")
        passed += 1
    except Exception as error:
        print(f"FAIL  {name}: {type(error).__name__}: {str(error).strip()}")
        failed += 1


username = input("Uživatelské jméno: ")
password = getpass.getpass("Heslo: ")
cislo_jidelny = input("Číslo jídelny: ")

print("\nVeřejné endpointy:")
run("Public.canteens", Public.canteens)
run("Public.search_canteens", lambda: Public.search_canteens(cislo_jidelny))
run("Public.canteen", lambda: Public.canteen(cislo_jidelny))
run("Public.s5url", lambda: Public.s5url(cislo_jidelny))
run("Public.version", lambda: Public.version(cislo_jidelny))
run("Public.version_info", lambda: Public.version_info(cislo_jidelny))
run("Public.menu", lambda: Public.menu(cislo_jidelny))
run("Public.menu_days", lambda: Public.menu_days(cislo_jidelny))
run("Public.menu_page", lambda: Public.menu_page(cislo_jidelny))

try:
    strava = Strava.login(username, password, cislo_jidelny)
    print("PASS  Strava.login")
    passed += 1
except Exception as error:
    print(f"FAIL  Strava.login: {error}")
    failed += 1
    strava = None

if strava:
    print("\nPřihlášené endpointy:")
    meals = []
    run("menu", strava.menu)
    run("meals", lambda: meals.extend(strava.meals()))
    run("days", strava.days)
    run("menu_today", strava.menu_today)
    run("ordered_meals", strava.ordered_meals)
    if meals:
        run("meal_details", lambda: strava.meal_details(meals[0]))
    run("user_info", strava.user_info)
    run("properties", strava.properties)
    run("username", lambda: strava.username)
    run("balance", strava.balance)
    run("canteen", strava.canteen)
    run("history", strava.history)
    run("payments", strava.payments)
    run("payment_qr", strava.payment_qr)
    run("issued_meals", strava.issued_meals)
    run("protocol", strava.protocol)
    run("enrollment_form", strava.enrollment_form)
    run("messages", strava.messages)
    run("unread_count", strava.unread_count)
    run("export_ics", strava.export_ics)

    if WRITE:
        print("\nZápisové endpointy (změny se na konci zahodí):")
        target = next((meal for meal in meals if meal.can_order or meal.can_cancel), None)
        if target:
            run("set_meal_count", lambda: strava.set_meal_count(target, 0 if target.ordered else 1))
        run("discard_changes", strava.discard_changes)
        run("save_orders", strava.save_orders)

    print("\nOdhlášení:")
    run("logout", strava.logout)

print(f"\n{passed} PASS, {failed} FAIL")
