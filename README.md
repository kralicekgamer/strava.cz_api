# Strava.cz rest API
## Info 
Toto je **neoficiální** rest api pro stravu.cz. V tomto dokumentu je popsáno vše co potřebuješ vědet o tomto API. Je zde také vysvětleno dopodrobna jak to celé funguje.

# Docs
## Instalace API
API nainstalujeme přes PyPI

```
pip install strava.cz_api
```

## Import API
Na začátku tvé aplikace je nutné importovat API.

```py
from api import StravaApi
```

## Autorizace
Na začátku všeho je nutné se autorizovat. Komunikace se serverem probíhá pomocí SID a cookies. To je nutné získat. 

### Script
Jedna možnost získání SID je pomocí automatizovaného scriptu.

Importujeme API a classu na getnutí SID tokenu, poté vytvoříme objekt autorization_token. Nakonec zavoláme metodu .getSid(), která vrátí náš token.

```py
from api import StravaApi, Sid

autorization_token = Sid("{username}", "{password}", {cislo_jidelny})
print(autorization_token.getSid())
```

### Manuálně
1. Otevřeme strava.cz
2. Přihlásíme se
3. Otevřeme devtools>network
4. Reload page.
5. Otevřeme `nactiVlastnostiPA`
6. Headers>cookies. Payload>SID. Vložíme do kódu.


## Initializace
Jakmile máme cookies a SID můžeme initializovat autorizaci v našem scriptu. 

```py
from api import StravaApi

api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")
```

- SID(str) - identifikační klíč komunikace, getnout pomocí Sid.getSid() nebo manuálně z dev tools, nutné
- cislo_jidelny(int) - číslo naší jídelny na kterou se přihlašujeme, nutné
- cookies(str) - můžeme vyplnit custom, ve většině případů - `NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D"`

Momentálně jsme vytvořili náš objekt `api_session`. Je nutné mít **validní SID**. Také je nutné mít správné cookies, aby komunikace správně fungovala.

**Examples jsou ve složce ./examples**

## Metody
Toto API má mnoho metod volání API endpointů. V následující části si rozebereme každou, jak ji použít a co vrátí. 

**Examples jsou ve složce ./examples**

## Public.getJidelnicek
- Vrátí jídelníček v json formátu. Pouze potřeba číslo jídelny. 
- Nutné importovat public.

```py
# importujeme class public
from api import Public

# vytiskneme jídelníček
print(Public.getJidelnicek("6218"))
```

### .getJidelnicekToday
- Vrátí dnešní jídelníček v JSON formátu.

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint
jidelnicek = api_session.getJidelnicekToday()

# vytiskneme náš jídelníček
print(jidelnicek)
```

### .getJidelnicekAll
- Vrátí celý jídelníček v JSON formátu

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint
jidelnicek = api_session.getJidelnicekAll()

# vytiskneme náš jídelníček
print(jidelnicek)
```

### .getUsername
- Vrátí uživatelské jméno.

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint
user = api_session.getUsername()

# vytiskneme uzivatelske jmeno
print(user)
```

### .getInfo
- Vrátí jídelníček v json struktuře.

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint
info = api_session.getInfo()

# vytiskneme info o uživateli a jídelně
print(info)
```

### .getJidelna
- Získá informace o jídělně

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint
info = api_session.getJidelna()

# vytiskneme info o jídelně
print(info)
```

### .getHistorieKlienta
- Získá info o historii objednávek klienta v určitém měsíci.
- date(str) = počáteční datum měsíce. 
    - 2025-01-01 - leden
    - 2025-12-01 - prosinec

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint
info = api_session.getHistorieKlienta("2025-01-01")

# vytiskneme historii obejnávek klienta
print(info)
```

### .getPlaby
- Vrátí pohyby na klientovém účtu

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint
info = api_session.getPlaby()

# vytiskneme pohyby na klientovém účtu
print(info)
```

### .getMessages
- Získá informace z jídelny

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint
info = api_session.getMessages()

# vytiskneme informace z jídelny
print(info)
```

### .postJidlo
- Přihlásí nebo ohlásí jídlo
- veta(int) - číslo itemu co chceme přihlásit
- stav(int) - 0 - odhlásit, 1 - přihlásit

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint, přihlásíme veta 5
api_session.postJidlo(5, 1)
```

**!!Objednávky je nutné uložit!!** viz. postOrders()

### .postDen
- Přihlásí nebo ohlásí celý den
- datum(str) = datum dne jaký chceme odhlásit. 2025-12-30
- stav(int) - 0 - odhlásit, 1 - přihlásit

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint, přihlásíme 2025-12-30
api_session.postDen("2025-12-30", 1)
```

**!!Objednávky je nutné uložit!!** viz. postOrders()

### .postOrders
- Uloží naše změny. 
- Po použití metod postDen() a postJidlo() je nutné uložit naše změny a poslat je na server.

```py
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D")

# zavoláme endpoint, přihlásíme veta 5
api_session.postJidlo(5, 1)

# uložíme změny
api_session.postOrders()
```

# Vysvětlení
Tento skript slouží k simulaci volání API endpointů používaných službou strava.cz. Každý požadavek musí obsahovat SID. Bez něj server požadavek odmítne. Každá akce ve webovém rozhraní (např. načtení jídelníčku, přihlášení oběda nebo uložení objednávky) odpovídá jednomu volání určitého API endpointu.

## GET requesty
Při volání endpointů typu GET (například getJidelnicek) klient odešle dotaz, který musí vždy obsahovat platný SID a současně cookies uložené při přihlášení. Server poté na základě těchto údajů ověří identitu uživatele a vrátí odpověď ve formátu JSON. Tento JSON obsahuje například dostupné obědy, ceny nebo aktuální stav objednávek. Nejde tedy o HTML stránku, ale o čistá data určená pro strojové zpracování.

## POST requesty
Endpointy typu POST se používají pro akce, kdy se odesílají změny nebo objednávky – typicky při přihlašování či odhlašování obědů.

1. Uživatel si na webu vybere obědy, které chce přihlásit nebo odhlásit.
2. Každý výběr odpovídá jednomu POST requestu, který se odešle spolu s aktuálními cookies.
3. Server na základě požadavku upraví cookies (např. uloží rozpracovanou objednávku) a pošle je zpět klientovi.
4. Klient může pokračovat ve výběru dalších jídel, přičemž se cookies s každým požadavkem aktualizují.
5. Po dokončení výběru se odešle finální požadavek – obvykle typu uložit objednávku –, který pošle upravené cookies zpět na server. Server poté objednávku zpracuje a potvrdí ji.
