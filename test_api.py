import getpass
from datetime import date

from strava_cz_api import Api, Auth, Public


def test(name, function):
    try:
        function()
        print(f"PASS  {name}")
        return True
    except Exception as error:
        print(f"FAIL  {name}: {error}")
        return False


username = input("Uživatelské jméno: ")
password = getpass.getpass("Heslo: ")
cislo_jidelny = input("Číslo jídelny: ")

passed = 0
failed = 0


def run(name, function):
    global passed, failed
    if test(name, function):
        passed += 1
    else:
        failed += 1


login = None

try:
    login = Auth.login(username, password, cislo_jidelny)
    print("PASS  Auth.login")
    passed += 1
except Exception as error:
    print(f"FAIL  Auth.login: {error}")
    failed += 1


if login:
    data, cookie = login
    sid, s5url = Auth.getCredentials(data)
    api = Api(sid, s5url, cislo_jidelny, cookie=cookie)

    run(
        "Auth.init",
        lambda: Auth.init(username, password, cislo_jidelny),
    )
    run("Auth.getCredentials", lambda: Auth.getCredentials(data))

    run("Public.getJidelny", Public.getJidelny)
    run("Public.getJidelnicek", lambda: Public.getJidelnicek(cislo_jidelny, "CZ"))
    run("Public.getJidelna", lambda: Public.getJidelna(cislo_jidelny))
    run("Public.getS5url", lambda: Public.getS5url(cislo_jidelny))
    run("Public.getVersion", lambda: Public.getVersion(cislo_jidelny))

    jidelnicek = api.getJidelnicekAll()
    jidelnicek_items = next(
        (items for items in jidelnicek.values() if isinstance(items, list) and items),
        [],
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

    run("Api.getJidelnicekAll", api.getJidelnicekAll)
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

    print("\nPOST endpointy mohou měnit objednávky:")
    if veta is not None:
        run("Api.postJidlo", lambda: api.postJidlo(veta, 0))
        run(
            "Api.postDen",
            lambda: api.postDen(date.today().isoformat(), 0),
        )
        run(
            "Api.getOrderModalDetails",
            lambda: api.getOrderModalDetails(
                veta,
                cislo_jidelnicku,
                datum_jidla,
                druh,
            ),
        )
        if vydejni_misto is not None:
            run(
                "Api.zmenVydejniMisto",
                lambda: api.zmenVydejniMisto(veta, vydejni_misto),
            )
        run("Api.zmenDietu", lambda: api.zmenDietu(veta, dieta))
    run("Api.zmenJazyk", lambda: api.zmenJazyk(api.lang))
    run("Api.postOrders", api.postOrders)
    run("Api.resetChanges", api.resetChanges)

    print("\nOdhlášení uživatele:")
    run("Api.logOut", api.logOut)

print(f"\n{passed} PASS, {failed} FAIL")
