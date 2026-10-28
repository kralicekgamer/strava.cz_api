"""
Příkazová řádka `strava-cz` (nebo `python -m strava_cz_api`).

Přihlašovací údaje se berou z proměnných prostředí STRAVA_USER, STRAVA_PASSWORD
a STRAVA_CANTEEN, jinak se na ně program zeptá.
"""
import argparse
import getpass
import json
import os
import sys
from dataclasses import asdict
from datetime import date, datetime

from . import __version__
from .client import Strava
from .errors import StravaError
from .public import Public


def _json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _dump(data):
    print(json.dumps(data, ensure_ascii=False, indent=2, default=_json_default))


def _meal_dict(meal):
    data = asdict(meal)
    data.pop("raw", None)
    data.update(ordered=meal.ordered, can_order=meal.can_order, can_cancel=meal.can_cancel)
    return data


def _print_meals(meals, as_json):
    if as_json:
        return _dump([_meal_dict(meal) for meal in meals])
    current = object()
    for meal in meals:
        if meal.date != current:
            current = meal.date
            print(f"\n{meal.date:%a %d.%m.%Y}" if meal.date else "\n(bez data)")
        mark = "✔" if meal.ordered else ("·" if meal.can_order else " ")
        price = f" – {meal.price:.2f} Kč" if meal.price else ""
        veta = f"[{meal.veta}] " if meal.veta else ""
        print(f"  {mark} {veta}{meal.meal_type or meal.course}: {meal.name}{price}")


def _login(args):
    username = os.environ.get("STRAVA_USER") or input("Uživatelské jméno: ")
    password = os.environ.get("STRAVA_PASSWORD") or getpass.getpass("Heslo: ")
    canteen = args.canteen or os.environ.get("STRAVA_CANTEEN") or input("Číslo jídelny: ")
    return Strava.login(username, password, canteen, lang=args.lang)


def _change(args, apply):
    with _login(args) as client:
        for item in args.items:
            apply(client, item)
        result = client.save_orders()
        if args.json:
            _dump(result)
        else:
            print("Uloženo.")


def build_parser():
    parser = argparse.ArgumentParser(prog="strava-cz", description="Neoficiální klient pro app.strava.cz")
    parser.add_argument("--version", action="version", version=f"strava-cz-api {__version__}")
    parser.add_argument("--json", action="store_true", help="výstup jako JSON")
    parser.add_argument("--lang", default="CZ", choices=["CZ", "EN", "SK"])
    parser.add_argument("--canteen", help="číslo jídelny (jinak STRAVA_CANTEEN)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("menu", help="jídelníček s objednávkami")
    p.add_argument("--date", help="jen jeden den (YYYY-MM-DD)")
    p.add_argument("--ordered", action="store_true", help="jen objednaná jídla")

    for name, text in (("order", "přihlásit jídla (veta)"), ("cancel", "odhlásit jídla (veta)"),
                       ("order-day", "přihlásit celé dny (YYYY-MM-DD)"),
                       ("cancel-day", "odhlásit celé dny (YYYY-MM-DD)")):
        sub.add_parser(name, help=text).add_argument("items", nargs="+")

    sub.add_parser("balance", help="stav konta")
    sub.add_parser("history", help="historie za měsíc").add_argument("month", nargs="?", help="YYYY-MM-DD")
    sub.add_parser("payments", help="platby")
    sub.add_parser("messages", help="zprávy")
    sub.add_parser("ics", help="export objednaných jídel do .ics").add_argument("file")
    sub.add_parser("canteens", help="vyhledat jídelnu (bez přihlášení)").add_argument("search", nargs="?", default="")
    sub.add_parser("public-menu", help="veřejný jídelníček (bez přihlášení)").add_argument("number")
    return parser


def run(args):
    if args.command == "canteens":
        rows = Public.search_canteens(args.search)
        if args.json:
            return _dump(rows)
        for row in rows:
            print(f"{row['number']:>6}  {row['name']} ({row['city']})")
        return
    if args.command == "public-menu":
        return _print_meals([m for d in Public.menu_days(args.number, args.lang) for m in d.meals], args.json)

    if args.command == "order":
        return _change(args, lambda client, veta: client.order(veta))
    if args.command == "cancel":
        return _change(args, lambda client, veta: client.cancel(veta))
    if args.command == "order-day":
        return _change(args, lambda client, day: client.order_day(day))
    if args.command == "cancel-day":
        return _change(args, lambda client, day: client.cancel_day(day))

    with _login(args) as client:
        if args.command == "menu":
            meals = client.menu_for(args.date) if args.date else client.meals()
            if args.ordered:
                meals = [meal for meal in meals if meal.ordered]
            _print_meals(meals, args.json)
        elif args.command == "balance":
            value = client.balance()
            _dump({"balance": value}) if args.json else print(f"Konto: {value} Kč")
        elif args.command == "history":
            _dump(client.history(args.month))
        elif args.command == "payments":
            _dump(client.payments())
        elif args.command == "messages":
            _dump(client.messages())
        elif args.command == "ics":
            client.export_ics(args.file)
            print(f"Uloženo do {args.file}")


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    try:
        run(args)
    except StravaError as error:
        print(f"Chyba Stravy #{error.number}: {error.message}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
