# made by OpiKula

from strava import Api, Auth
import getpass

# Ziskame od uzivatele credentials
username = input("Zadej zde svoje uživatelské jméno: ")
password = getpass.getpass("Zadej zde svoje heslo: ")
jidelna = input("Zadej zde číslo jídelny: ")

# Poslani post requestu a getnuti SID a s5url
cookie, data = Auth.login(username, password, jidelna)
sid, s5url = Auth.getCredentials(data)


# Inicializujeme spojeni a vytiskneme jidelnicek
example = Api(sid, s5url, jidelna)
print(example.getJidelnicekToday())