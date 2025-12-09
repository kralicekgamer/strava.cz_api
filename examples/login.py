# made by OpiKula

from api import StravaApi, Sid
import getpass

# Nastavime cookies
cookies = "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D"

# Ziskame od uzivatele credentials
username = input("Zadej zde svoje uživatelské jméno: ")
password = getpass.getpass("Zadej zde svoje heslo: ")
jidelna = int(input("Zadej zde číslo jídelny: "))

# Getneme SID
autorization_token = Sid(username, password, jidelna, "")
sid = autorization_token.getSid()

# Inicializujeme spojeni a vytiskneme jidelnicek
example = StravaApi(sid, jidelna, cookies, "", username)
print(example.getJidelnicekToday())