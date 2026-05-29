
from strava_cz_api import Api, Auth
import getpass
import json

username = input("Zadej uzivatelske jmeno: ").strip()
password = getpass.getpass("Zadej heslo: ")
cislo_jidelny = input("Zadej cislo jidelny: ").strip()

data, _ = Auth.login(username, password, cislo_jidelny)
sid, s5url = Auth.getCredentials(data)

api = Api(sid, s5url, cislo_jidelny)

print("Uzivatel:", api.getUsername())
print("Info:")
print(json.dumps(json.loads(api.getInfo()), indent=2, ensure_ascii=False))
print("Jidelna:")
print(json.dumps(json.loads(api.getJidelna()), indent=2, ensure_ascii=False))
