# Strava.cz rest API
> ⚠️ **UPOZORNĚNÍ:** Strava.cz má vysoce proměnlivé prostředí (každá jídelna má jiný počet obědů, jiné názvy chodů apod.) z toho důvodu toto API **není plně univerzální**. I když jsem se snažil ho napsat univerzálně, nějaké metody nemusí plně fungovat a bude to vyžadovat vaší opravu. 

Toto je **neoficiální** REST api pro stravu.cz. V tomto dokumentu je popsáno vše co potřebuješ vědet o tomto API. Je zde také vysvětleno dopodrobna jak to celé funguje.

## Instalace
```bash
pip install strava_cz_api
```

| Verze | Stav | Poznámka |
| --- | --- | --- |
| **1.X** | ❌ | Stará verze bez error handlingu. Funkční :D |
| **2.0 - **2.5** | ⚠️ | Mnoho bugů v POST requestech a práci s cookies. |
| **2.5.1** | ⚠️ | Nelze importovat public class. |
| **2.5.2** | ✅ | 

## Autentizace
K API endpointům potřebuješ **SID** a **s5url**. Můžeš si je získat sám z dev tools v prohlížeči, ale nejlepší cesta je pomocí metod: `Auth.login()` a `Auth.getCredentials()`:

```py
from strava_cz_api import Auth

data, cookie = Auth.login("demo", "demo", "0000")
sid, s5url = Auth.getCredentials(data)
```

**Poznámky:**
- Podporované jazyky: `CZ`, `EN`, `SK`.
- `Auth.login()` vrací `cookie` a JSON data; `Auth.getCredentials()` z nich vytáhne `sid` a `s5url`.

## Inicializace API
```py
from strava_cz_api import Api

api = Api(
    sid="00000000000000000000000000000000",
    s5url="", 
    cislo_jidelny="0000"
)
```

> ⚠️ `s5url=""` může být hash, url či prázdné. Někdy se stane, že musí být spravný input, někdy může být prázné. 


## Veřejné endpointy (bez přihlášení)

| Metoda | Popis | Poznámka |
| --- | --- | --- |
| `getJidelny()` | Seznam jídelen
| `getJidelna()` | Informace o jídělne
| `getS5url()` | URL jídelny
| `getJidelnicek()` | Get veřejného jídelníčku 
| `getVersion()` | Verze softwaru jídelny 

## Autentizované endpointy (Api)
| Metoda | Popis | Poznámka |
| --- | --- | --- |
| `getJidelnicekToday()` | Dnešní jídelníček | Vrací list (`table0`) |
| `getJidelnicekAll()` | Kompletní jídelníček 
| `getInfo()` | Informace o uživateli | Upravený payload.
| `getUsername()` | Uživatelské jméno | Vytahuje z `getInfo()` |
| `getJidelna()` | Informace o jídelně 
| `getHistorieKlienta(date)` | Historie objednávek za měsíc | `date` = první den měsíce (např. `2025-01-01`) |
| `getPlaby()` | Pohyby na účtu
| `getMessages()` | Zprávy pro uživatele 
| `getProtokol()` | Vrátí protokol
| `getVydej()` | Vrátí list vydaných jídel.
| `postJidlo(veta, stav)` | Přihlásit/odhlásit jídlo | `stav`: 1 přihlásit, 0 odhlásit |
| `postDen(datum, stav)` | Přihlásit/odhlásit celý den | `datum` ve formátu `YYYY-MM-DD` |
| `postOrders()` | Uložit změny objednávek | Nutné po `postJidlo`/`postDen` |
| `resetChanges()` | Resetuje neuložené změny v komunikaci. | Dobré pro zrušení změn při objednávkách

## Filtr
Filtr pro data existuje, ale bude se dále rozšiřovat. Lze ho importovat (`from strava_cz_api import Filter`), ale zatím není zaručeno, že všude funguje správně.

```py
from strava_cz_api import Filter

filtrovano = Filter.filter_json(["veta"], api.getJidelnicekAll())
print(filtrovano)
```

## Objednávky – správný postup
> ⚠️ Postup u každé jídelný se může lišit. 
Změny objednávek se ukládají ve dvou krocích:
1. Provedení změn (`postJidlo` nebo `postDen`)
2. Uložení (`postOrders`)

```py
data, cookie = api.postJidlo(5, 1)

data, cookie = api.postOrders()
```

Nebo lze resetovat změny:
```py
data, cookie = api.resetChanges()
```

## Návratové hodnoty
- Většina metod vrací JSON string.
- POST metody `postJidlo()`, `postDen()`, `postOrders()`, `resetChanges()` a `Auth.login()` vrací **dvojici `(data, cookie)`** z POST odpovědi.
  - `data` - JSON response z API
  - `cookie` - nový cookie pro další požadavky (automaticky se aktualizuje v Api objektu) 

> ⚠️ Je tedy potřeba buďto nepoužívat návratové hodnoty nebo jednu z nich vrátit do prázdné proměnné (např. _). Pokud vrátíte do jedné hodnoty vrátí se vám tupple a kód pravděpodobně někde spadne.

## Chyby
- Error handling je dostupný přes výjimky, které lze importovat: `from strava_cz_api import StravaError`.
- Při neúspěšném požadavku se vyhazuje `ConnectionError`.

## Příklady
Ukázkové skripty najdeš ve složce `./examples`.

## Json struktura 
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
            "alergeny": [], // alergeny
            "chod": "C", // číslo chodu (A = snídaně, B, C)
            "druh": "OB", // druh chodu ve zkratce
            "cena": "45.00", // cena
            "polevka": "N", // zda pole je polévka (je v ceně)
            "pocet": 1, // 1 = přihlášeno, 0 = odhlášeno
            "veta": "172", // id políčka
            "vetaDieta": "196", // ??
            "omezeniObj": { // ???
                "den": "",
                "obj": "",
                "zm": "", 
                "bur": "C" 
            },
            "burza": { // ???
                "zmena": "0",
                "ostatni": "0",
                "nabidka": "0",
                "poptavka": "0"
            },
            "vydejniMisto": { // kde se vydává oběd (škola má více jídelních budov)
                "misto": "2",
                "mista": "2"
            },
            "diety": { // ??
                "dieta": "",
                "diety": ""
            },
            "zkratkaProduktu": "OB", // zkratka produktu (identické jako chod, u polévky chybí??)
            "cisloJidelnicku": "1", // ??
            "multipleNazev": "1NOběd č. 1COB", // ??
            "version": 5, // ??
            "casKonec": "2026-06-29T11:50:00", // do kdy lze přihlásit
            "casOdhlaseni": "2026-06-29T11:50:00", // do kdy lze přihlásit
            "obrazky": []
        },
        ...
    ]
}
```
- Mnoho polí není vyplněno. Zda víte co to je, doplňte to nebo mě kontaktujte.

## Strava verze
- Zaznamenané strava verze společně s poznámkami. Seřazeno od nejpoužívanějších
| Verze | Poznámka |
| --- | --- |
| 5.14 | 
| 5.13 | Vytvářeno. Testováno.
| 4.65 | 
| 4.64 | 
| 4.00 | 
| 5.12 | 
| 5.15 | 
| 5.11 | 
| 4.51 | Demo verze. Testováno. Nějaké metody nefungují. 

- Největší rozdíly jsou většinou mezi verzí 4 a 5. Endpointy a outputy jsou podobné. 
- Pravděpodobně od verze 5 je vyžadováno `s5url`
- Mnoho polí není vyplněno. Pokud máte nějaké poznamky. Doplňte je nebo mě kontaktujte.

## Demo
- Demo uživatele si lze vytvořit na https://www.strava.cz/strava/Stravnik/Demo
- Poté se lze přihlásit na https://app.strava.cz/ na jídelně `0000`
- Prosím nepoužívejte `demo` `demo`. Pak je to zablokované a nefunguje to :D.
