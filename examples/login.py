# made by OpiKula

from strava_cz_api import Api, Auth, StravaError
import getpass

# Ziskame od uzivatele credentials
username = input("Zadej zde svoje uživatelské jméno: ")
password = getpass.getpass("Zadej zde svoje heslo: ")
jidelna = input("Zadej zde číslo jídelny: ")

# Poslani post requestu a getnuti SID a s5url
try:
    data, _ = Auth.login(username, password, jidelna)

except StravaError:
    print("Chybné heslo")
    exit()

# ziskame sid a s5url
sid, s5url = Auth.getCredentials(data)

# Inicializujeme spojeni a vytiskneme jidelnicek
example = Api(sid, s5url, jidelna)


print(example.getJidelnicekToday())