from strava import Public
import json

cislo_jidelny = input("Zadej cislo jidelny: ").strip()
lang = (input("Jazyk (CZ/EN/SK) [CZ]: ").strip() or "CZ").upper()

data = Public.getJidelnicek(cislo_jidelny, lang)
jidelnicek = json.loads(data)

print(json.dumps(jidelnicek, indent=2, ensure_ascii=False))
