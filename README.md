# Strava.cz rest API
> ⚠️ **UPOZORNĚNÍ:** Strava.cz má vysoce proměnlivé prostředí (každá jídelna má jiný počet obědů, jiné názvy chodů apod.) z toho důvodu toto API **není plně univerzální**. Některé metody nemusí na tvé jídelně fungovat.

Toto je **neoficiální** Python API pro [app.strava.cz](https://app.strava.cz). Kompletní seznam metod s popisem, endpointy a ukázkami je v **[HTML dokumentaci](docs/index.html)**.

## Instalace
```bash
pip install strava-cz-api
```

| Verze | Stav | Poznámka |
| --- | --- | --- |
| **1.X** | ❌ | Stará verze bez error handlingu. |
| **2.0 - 2.5.2** | ⚠️ | Nedoladěné verze. Hodně chyb. |
| **2.5.3 - 2.5.7** | ✅ | |
| **3.0.0** | 🚧 | Nové API, staré metody fungují jako deprecated aliasy. |

## Rychlý start
```py
from strava_cz_api import Strava

with Strava.login("jmeno", "heslo", "0000") as strava:
    for meal in strava.menu_today():
        print(meal.meal_type, meal.name, meal.price, "Kč", "✔" if meal.ordered else "")

    print("Konto:", strava.balance(), "Kč")
```

`with` se na konci sám odhlásí. Pokud už máš SID, klient vytvoříš i přímo: `Strava(sid, "0000", s5url)`.

> ℹ️ Číslo jídelny posílej jako string (`"0042"`). Podporované jazyky: `CZ`, `EN`, `SK`.

## Objednávky
Změny se ukládají ve dvou krocích – nejdřív změna, pak uložení:

```py
obed = next(m for m in strava.menu_for("2026-11-02") if m.can_order)
strava.order(obed)          # nebo cancel(), order_day(), cancel_day(), change_pickup_place()…
strava.save_orders()        # bez toho se nic neprojeví
# strava.discard_changes()  # zahodí neuložené změny
```

## Přehled metod

**`Strava` (přihlášený klient)**

| Oblast | Metody |
| --- | --- |
| Session | `Strava.login()`, `logout()`, `relogin()`, `set_language()` |
| Jídelníček | `menu()`, `meals()`, `days()`, `menu_for(day)`, `menu_today()`, `ordered_meals()`, `meal_details(meal)` |
| Objednávky | `order()`, `cancel()`, `set_meal_count()`, `order_day()`, `cancel_day()`, `change_pickup_place()`, `change_diet()`, `save_orders()`, `discard_changes()`, `rate_meal()` |
| Účet | `balance()`, `history(month)`, `payments()`, `payment_qr()`, `issued_meals()`, `user_info()`, `properties()`, `username`, `protocol()`, `enrollment_form()`, `attendance()`, `canteen()` |
| Zprávy | `messages()`, `unread_count()`, `message(id)`, `mark_read(*ids)`, `confirm_notice()` |
| Extra | `export_ics(path)` – objednané obědy do kalendáře |

**`Public` (bez přihlášení)**: `canteens()`, `search_canteens(text)`, `canteen(cislo)`, `s5url()`, `version()`, `version_info()`, `menu()`, `menu_days()`, `menu_page()`.

Metody jako `menu()` vrací přesně JSON ze Stravy (dict). `meals()`, `days()`, `menu_for()` vrací objekty `Meal` / `MenuDay` (datum jako `date`, cena jako `float`, `ordered`, `can_order`, `can_cancel`, `allergens`…). Původní data jsou v `meal.raw`.

## Příkazová řádka
```bash
strava-cz canteens plzen
```
```bash
strava-cz menu --date 2026-11-02
```
```bash
strava-cz order 172 173
```

Další příkazy: `cancel`, `order-day`, `cancel-day`, `balance`, `history`, `payments`, `messages`, `ics`, `public-menu`. Přihlašovací údaje se berou z `STRAVA_USER`, `STRAVA_PASSWORD`, `STRAVA_CANTEEN`, jinak se program zeptá. `--json` vypíše JSON.

## Chyby
Všechny výjimky dědí z `StravaError` a mají `number`, `message` a `response`. Vypršelé SID vyhodí `SessionExpiredError` (a s `Strava.login(..., auto_relogin=True)` se klient sám znovu přihlásí). Síťové chyby vyhazují `StravaConnectionError`.

| Číslo chyby | Název chyby | Popis |
| --- | --- | --- |
| `6` | `JidelnaNenalezenaError` | Chybné číslo jídelny |
| `13, 90, 1009–1011, 1014, 10104` | `SessionExpiredError` | Relace skončila |
| `14` | `NelzeVytvoritSID` | |
| `15` | `ChybneSID` | Chybný SID token |
| `20` | `UserBlockedError` | Strávník je zablokován |
| `30` | `S5AndJidelnaPayload` | Nesedí S5URL a číslo jídelny |
| `35` | `NelzePrihlasit` | |
| `998` | `Timeout` | |
| `3002` | `BackendError` | Software jídelny je mimo provoz / endpoint na této verzi neexistuje |
| `10102` | `AuthError` | Neplatné SID (např. po 60 dnech nečinnosti) |
| `13201` | `S5Payload` | Špatná S5URL |
| `13404` | `ChybnyUzivatel` | Chybné uživatelské jméno |
| `13405` | `ChybneHesloError` | Chybné heslo |
| `13410` | `LoginTimeout` | Login timeout na 2 h |
| ostatní `≥ 99` | `ApiError` | Chyba odchycena u stravy.cz |

## Migrace z 2.x
Staré `Api`, `Auth` a názvy metod fungují dál, jen vypíšou `DeprecationWarning`. Hlavní změny:
- Jedna HTTP session pro všechny requesty, cookies se drží samy. Metody vrací jen data, nikdy `(data, cookie)`.
- `Auth.login()` + `Auth.getCredentials()` + `Api(...)` → `Strava.login()`.
- `getJidelnicekAll` → `menu`, `postJidlo` → `order`/`cancel`, `postDen` → `order_day`/`cancel_day`, `postOrders` → `save_orders`, `resetChanges` → `discard_changes`, `getPlatby` → `payments`, `getVydej` → `issued_meals`…
- `logOut()` dřív volal logovací endpoint `/api/logger`, nově `logout()` opravdu odhlásí přes `/api/logOut`.

Celá tabulka je v [dokumentaci](docs/index.html#migrace).

## Testy
Offline unit testy (bez sítě):
```bash
python -m unittest discover tests
```

Živý test proti Stravě (zeptá se na jméno, heslo a jídelnu). Bez `--write` jen čte, s `--write` zkusí i změnu objednávky a hned ji zahodí:
```bash
python test_api.py
```

## Strava verze

| Verze | Funkčnost | Poznámka |
| --- | --- | --- |
| 5.15 | ❔ |
| 5.14 | ✅ | Nejsou implementovány metody pro burzu. |
| 5.13 | ⭐ |
| 5.12 | ❔ |
| 5.11 | ❔ |
| 4.65 | ❔ |
| 4.64 | ❔ |
| 4.51 | ⚠️ | Nefunkční: `canteen`, `protocol`, objednávky, `save_orders` (S4 potřebuje XML změn), `discard_changes` |
| 4.00 | ❔ |

- ⭐ - stavěno na této verzi
- ✅ - funkční
- ⚠️ - problémy
- ❔ - neotestováno

## Json struktura (s5.13)
Jedno jídlo z `menu()` (`objednavky`):
```json
{
    "tableX": [
        {
            "id": 0,
            "datum": "30.06.2026", // datum
            "druh_popis": "Polévka", // část
            "druh_chod": "Oběd", // chod
            "nazev": "Polévka 1", // název chodu (oběd č. 1, Řízek)
            "popis": "Snídaně", // popis chodu
            "delsiPopis": "", // delší popis chodu
            "zakazaneAlergeny": null, // ??
            "alergeny_text": "", // alergeny
            "alergeny": [["01", "Obiloviny obsahující lepek"]], // alergeny [kód, název]
            "chod": "C", // číslo chodu (A=snídaně, B=svačina, C=oběd/balíček, D=svačina, E=večeře, F=druhá večeře)
            "druh": "OB", // druh chodu ve zkratce
            "cena": "45.00", // cena
            "polevka": "N", // zda pole je polévka (je v ceně)
            "pocet": 1, // 1 = přihlášeno, 0 = odhlášeno
            "veta": "172", // id políčka
            "vetaDieta": "196", // ??
            "omezeniObj": {
                "den": "", // CO - ?, VP - ?
                "obj": "", // C - Nelze objednat, I - Vždy přihlášeno (polévka), V - Svátek
                "zm": "", // C - Nelze změnit, I - Vždy přihlášeno (polévka)
                "bur": "C" // C - Nelze obchodovat, ! - ? , I - Vždy přihlášeno (polévka), V - Svátek
            },
            "burza": { // poptávání a nabízení jídel, od verze 5.14
                "zmena": "0",
                "ostatni": "0",
                "nabidka": "0",
                "poptavka": "0"
            },
            "vydejniMisto": { // kde se vydává oběd (škola má více jídelních budov)
                "misto": "2",
                "mista": "2"
            },
            "diety": {
                "dieta": "",
                "diety": ""
            },
            "zkratkaProduktu": "OB",
            "cisloJidelnicku": "1", // potřeba pro detail a hodnocení jídla
            "multipleNazev": "1NOběd č. 1COB", // ??
            "version": 5, // verze stravy (4/5)
            "casKonec": "2026-06-29T11:50:00", // do kdy lze přihlásit
            "casOdhlaseni": "2026-06-29T11:50:00", // do kdy lze odhlásit
            "obrazky": []
        }
    ]
}
```

## Forks
- Pokud chcete doplnit readme, otestovali jste verzi, máte poznámky nebo upravujete kód, github pull request.

## Demo
- Demo uživatele si lze vytvořit na https://www.strava.cz/strava/Stravnik/Demo
- Poté se lze přihlásit na https://app.strava.cz/ na jídelně `0000`
- Demo uživatel se smaže začátkem nového měsíce

## Todo
- [x] /api/logOut (opravené odhlášení)
- [ ] Burza (nabídka/poptávka jídel)
- [ ] /api/ulozNastaveniKlienta, /api/zapisNastaveniS5 (nastavení strávníka – XML s hashem, subscribe mailů funguje random :D)
- [ ] `save_orders()` pro S4 jídelny (posílá XML změn)
