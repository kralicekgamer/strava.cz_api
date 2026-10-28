from strava_cz_api import Public

hledat = input("Hledat jídelnu (název/město/číslo): ").strip()
for jidelna in Public.search_canteens(hledat)[:10]:
    print(f"{jidelna['number']:>6}  {jidelna['name']} ({jidelna['city']})")

cislo_jidelny = input("Zadej cislo jidelny: ").strip()
lang = (input("Jazyk (CZ/EN/SK) [CZ]: ").strip() or "CZ").upper()

for den in Public.menu_days(cislo_jidelny, lang):
    print(f"\n{den.date:%d.%m.%Y}")
    for meal in den.meals:
        alergeny = ", ".join(code for code, _ in meal.allergens)
        print(f"  {meal.course}: {meal.name}  [{alergeny}]")
