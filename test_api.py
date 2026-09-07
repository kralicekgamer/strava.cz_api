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

    run("Auth.getCredentials", lambda: Auth.getCredentials(data))

    run("Public.getJidelnicek", lambda: Public.getJidelnicek(cislo_jidelny, "CZ"))
    run("Public.getJidelna", lambda: Public.getJidelna(cislo_jidelny))
    run("Public.getS5url", lambda: Public.getS5url(cislo_jidelny))
    run("Public.getVersion", lambda: Public.getVersion(cislo_jidelny))
    run("Api.getJidelnicekAll", api.getJidelnicekAll)
    run("Api.getJidelnicekToday", api.getJidelnicekToday)
    run("Api.getInfo", api.getInfo)
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

    print("\nPOST endpointy mohou měnit objednávky:")
    run("Api.postOrders", api.postOrders)
    run("Api.resetChanges", api.resetChanges)

print(f"\n{passed} PASS, {failed} FAIL")
