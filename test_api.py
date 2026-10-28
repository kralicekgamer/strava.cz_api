import getpass
import os
import sys
from datetime import date

from strava_cz_api import Api, Auth, BackendError, Public


if os.name == "nt":
    os.system("")

USE_COLORS = sys.stdout.isatty()
GREEN = "\033[92m" if USE_COLORS else ""
RED = "\033[91m" if USE_COLORS else ""
YELLOW = "\033[93m" if USE_COLORS else ""
CYAN = "\033[96m" if USE_COLORS else ""
RESET = "\033[0m" if USE_COLORS else ""


def color(text, value):
    return f"{value}{text}{RESET}"


def report_backend_error(name, error):
    message = str(error).strip() or error.__class__.__name__
    print(f"{color('!', YELLOW)} {name}")
    print(f"    Odpověď Stravy: {message}")
    print(f"    {color('Verze Stravy není kompatibilní', YELLOW)}")


def test(name, function):
    try:
        result = function()
        print(f"{color('✓', GREEN)} {name}")
        return "pass", result
    except BackendError as error:
        report_backend_error(name, error)
        return "incompatible", None
    except Exception as error:
        message = str(error).strip() or error.__class__.__name__
        print(f"{color('✗', RED)} {name}: {message}")
        return "fail", None


username = input("Uživatelské jméno: ")
password = getpass.getpass("Heslo: ")
cislo_jidelny = input("Číslo jídelny: ")

passed = 0
failed = 0
incompatible = 0


def run(name, function):
    global passed, failed, incompatible
    status, result = test(name, function)
    if status == "pass":
        passed += 1
    elif status == "incompatible":
        incompatible += 1
    else:
        failed += 1
    return result


def section(title):
    print(f"\n{color(f'--- {title} ---', CYAN)}")


login = None

section("Autentizace")
try:
    login = Auth.login(username, password, cislo_jidelny)
    print(f"{color('✓', GREEN)} Auth.login")
    passed += 1
except BackendError as error:
    report_backend_error("Auth.login", error)
    incompatible += 1
except Exception as error:
    print(f"{color('✗', RED)} Auth.login: {str(error).strip()}")
    failed += 1


if login:
    data, cookie = login
    sid, s5url = Auth.getCredentials(data)
    api = Api(sid, s5url, cislo_jidelny, cookie=cookie)

    run("Auth.init", lambda: Auth.init(username, password, cislo_jidelny))
    run("Auth.getCredentials", lambda: Auth.getCredentials(data))

    section("Veřejné endpointy")
    run("Public.getJidelny", Public.getJidelny)
    run("Public.getJidelnicek", lambda: Public.getJidelnicek(cislo_jidelny, "CZ"))
    run("Public.getJidelna", lambda: Public.getJidelna(cislo_jidelny))
    run("Public.getS5url", lambda: Public.getS5url(cislo_jidelny))
    run("Public.getVersion", lambda: Public.getVersion(cislo_jidelny))

    section("Načtení jídelníčku")
    jidelnicek = run("Api.getJidelnicekAll", api.getJidelnicekAll)
    jidelnicek_items = (
        next(
            (items for items in jidelnicek.values() if isinstance(items, list) and items),
            [],
        )
        if isinstance(jidelnicek, dict)
        else []
    )
    prvni_jidlo = jidelnicek_items[0] if jidelnicek_items else {}
    veta = prvni_jidlo.get("veta")
    cislo_jidelnicku = prvni_jidlo.get("cisloJidelnicku")
    datum_jidla = prvni_jidlo.get("datum", date.today().isoformat())
    druh = prvni_jidlo.get("druh")
    vydejni_misto_data = prvni_jidlo.get("vydejniMisto")
    vydejni_misto = (
        vydejni_misto_data.get("misto")
        if isinstance(vydejni_misto_data, dict)
        else None
    )
    diety_data = prvni_jidlo.get("diety")
    dieta = diety_data.get("dieta", "") if isinstance(diety_data, dict) else ""

    section("Autentizované GET endpointy")
    run("Api.getJidelnicekToday", api.getJidelnicekToday)
    run("Api.userInfo", api.userInfo)
    run("Api.getInfo", api.getInfo)
    run("Api.getInfo(resetTables=True)", lambda: api.getInfo(resetTables=True))
    run("Api.getInfo(resetTables=False)", lambda: api.getInfo(resetTables=False))
    run("Api.getUsername", api.getUsername)
    run("Api.getJidelna", api.getJidelna)
    run(
        "Api.getHistorieKlienta",
        lambda: api.getHistorieKlienta(date.today().replace(day=1).isoformat()),
    )
    run("Api.getPlatby", api.getPlatby)
    run("Api.getMessages", api.getMessages)
    run("Api.getProtokol", api.getProtokol)
    run("Api.getVydej", api.getVydej)
    run("Api.getQrPlatba", api.getQrPlatba)
    run(
        "Api.getPoctyJidel",
        lambda: api.getPoctyJidel(date.today().isoformat()),
    )
    run("Api.getProdej", api.getProdej)
    run("Api.getMessagesAmount", api.getMessagesAmount)

    section("Autentizované objednávkové endpointy")
    run("Api.postJidlo", lambda: api.postJidlo(veta or "", 0))
    run("Api.postDen", lambda: api.postDen(date.today().isoformat(), 0))
    run(
        "Api.getOrderModalDetails",
        lambda: api.getOrderModalDetails(
            veta or "",
            cislo_jidelnicku or "",
            datum_jidla,
            druh or "",
        ),
    )
    run(
        "Api.zmenVydejniMisto",
        lambda: api.zmenVydejniMisto(veta or "", vydejni_misto or ""),
    )
    run("Api.zmenDietu", lambda: api.zmenDietu(veta or "", dieta))
    run("Api.zmenJazyk", lambda: api.zmenJazyk(api.lang))
    run("Api.postOrders", api.postOrders)
    run("Api.resetChanges", api.resetChanges)

    section("Odhlášení")
    run("Api.logOut", api.logOut)

section("Souhrn")
print(
    f"{color('✓ PASS', GREEN)}: {passed}  "
    f"{color('✗ FAIL', RED)}: {failed}  "
    f"{color('! NEKOMPATIBILNÍ', YELLOW)}: {incompatible}"
)
