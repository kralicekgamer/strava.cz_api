# Strava.cz rest API
> ⚠️ **UPOZORNĚNÍ:** Strava.cz má vysoce proměnlivé prostředí (každá jídelna má jiný počet obědů, jiné názvy chodů apod.) z toho důvodu toto API **není plně univerzální**. I když jsem se snažil ho napsat univerzálně, nějaké metody nemusí plně fungovat a bude to vyžadovat vaší opravu. 

Toto je **neoficiální** REST api pro stravu.cz. V tomto dokumentu je popsáno vše co potřebuješ vědet o tomto API. Je zde také vysvětleno dopodrobna jak to celé funguje.

## Instalace
```bash
pip install strava.cz_api
```

## Autentizace
K API endpointům potřebuješ **SID** a **s5url**. Můžeš si je získat sám z dev tools v prohlížeči, ale nejlepší cesta je pomocí metod: `Auth.login()` a `Auth.getCredentials()`:

```py
from strava import Auth

cookie, data = Auth.login("demo", "demo", "0000")
sid, s5url = Auth.getCredentials(data)
```

**Poznámky:**
- Podporované jazyky: `CZ`, `EN`, `SK`.
- `Auth.login()` vrací `cookie` a JSON data; `Auth.getCredentials()` z nich vytáhne `sid` a `s5url`.

## Inicializace API
```py
from strava import Api

api = Api(
    sid="00000000000000000000000000000000",
    s5url="", 
    cislo_jidelny="0000"
)
```

**Poznámky:**
- `s5url=""` může být hash, url či prázdné. Někdy se stane, že musí být spravný input, někdy může být prázné. 

## Veřejné endpointy (bez přihlášení)

| Metoda | Popis | Poznámka |
| --- | --- | --- |
| `getJidelny()` | Seznam jídelen
| `getJidelna()` | Informace o jídělne
| `getS5url()` | URL jídelny
| `getJidelnicek()` | Get veřejného jídelníčku 

## Autentizované endpointy (Api)
| Metoda | Popis | Poznámka |
| --- | --- | --- |
| `getJidelnicekToday()` | Dnešní jídelníček | Vrací list (`table0`) |
| `getJidelnicekAll()` | Kompletní jídelníček 
| `getInfo()` | Informace o uživateli
| `getUsername()` | Uživatelské jméno | Vytahuje z `getInfo()` |
| `getJidelna()` | Informace o jídelně 
| `getHistorieKlienta(date)` | Historie objednávek za měsíc | `date` = první den měsíce (např. `2025-01-01`) |
| `getPlaby()` | Pohyby na účtu
| `getMessages()` | Zprávy pro uživatele 
| `postJidlo(veta, stav)` | Přihlásit/odhlásit jídlo | `stav`: 1 přihlásit, 0 odhlásit |
| `postDen(datum, stav)` | Přihlásit/odhlásit celý den | `datum` ve formátu `YYYY-MM-DD` |
| `postOrders()` | Uložit změny objednávek | Nutné po `postJidlo`/`postDen` |

## Objednávky – správný postup
Změny objednávek se ukládají ve dvou krocích:
1. Provedení změn (`postJidlo` nebo `postDen`)
2. Uložení (`postOrders`)

```py
cookie_data = api.postJidlo(5, 1)
cookie_data = api.postOrders()
```

## Návratové hodnoty
Většina metod vrací JSON string. Metody `postJidlo`, `postDen` a `postOrders` vrací dvojici `(cookie, data)` z POST odpovědi. 

## Chyby a omezení
- Při neúspěšném požadavku se vyhazuje `ConnectionError`.
- Některé jídelny mohou vyžadovat úpravy payloadů nebo cookie.

## Příklady
Ukázkové skripty najdeš ve složce `./examples`.

## Demo
- Demo uživatele si lze vytvořit na https://www.strava.cz/strava/Stravnik/Demo
- Poté se lze přihlásit na https://app.strava.cz/ na jídelně `0000`