# Strava.cz rest API
## Info 
Toto je **neoficiální** rest api pro stravu.cz. V tomto dokumentu je popsáno vše co potřebuješ vědet o tomto API. Je zde také vysvětleno dopodrobna jak to celé funguje.

# Docs
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

autorization_token = Sid("{username}", "{password}", {cislo_jidelny}, "{user_agent}")
print(autorization_token.getSid())
```

user_agent - **nutné získat z devtools**
- F12>konzole>napiš `navigator.userAgent`.
Vrátí se ti user_agent.


### Manuálně
1. Otevřeme strava.cz
2. Přihlásíme se
3. Otevřeme devtools>network
4. Reload page.
5. Otevřeme `nactiVlastnostiPA`
6. Headers>cookies. Payload>SID. Vložíme do kódu.


## Initializace
Jakmile máme cookies, user_agent a SID můžeme initializovat autorizaci v našem scriptu. 
from api import StravaApi

```py
from api import StravaApi

api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D", "Mozilla/5.0 (X11; Linux x86_64)")
```

Momentálně jsme vytvořili náš objekt `api_session`. Je nutné mít **validní SID**. Je také nutné mít správné cookies a user_agent.

- **Defaultní cookies:** `NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D"`

- Defaultní cookies lze využít. Pokud je potřeba, můžeme upravit.

**Examples jsou ve složce ./examples**

## Metody
Toto API má mnoho metod volání API endpointů. V následující části si rozebereme každou, jak ji použít a co vrátí. 

**Examples jsou ve složce ./examples**

### .getJidelnicek
- Endpoint `objednavky`
- Vrátí jídelníček v json struktuře.

```
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D", "Mozilla/5.0 (X11; Linux x86_64)", "user")

# zavoláme endpoint
jidelnicek = api_session.getJidelnicek()

# vytiskneme náš jídelníček
print(jidelnicek)
```


### .getInfo
- Endpoint `nactiVlastnostiPA`
- Vrátí jídelníček v json struktuře.

```
from api import StravaApi


# initializujeme spojení
api_session = StravaApi("00000000000000000000000000000000", "4242", "NEXT_LOCALE=cs; multiContextSession=%7B%22printOpen%22%3A%7B%22value%22%3Afalse%2C%22expiration%22%3A-1%7D%7D", "Mozilla/5.0 (X11; Linux x86_64)", "user")

# zavoláme endpoint
info = api_session.getInfo()

# vytiskneme info o uživateli a jídelně
print(info)
```

### .getJidelna
### .getHistorieKlienta
### .getPlaby
### .getMessages

### .postJidlo
### .postDen
### .postOrders

# Vysvětlení
Toto API volá endpointy na stravě.cz. Každý POST i GET request musí mít SID - komunikační prostředek klienta. Kterákoliv akce je zavolání API endpointu. Tento script simuluje volání endpointů. 

## GET
Pošle se GET request na určitý endpoint např. getJidelnicek. Tento request musí mít SID a cookies. Server request přijme a vrátí obsah v plain JSON textu. 

## POST
Zde je to trochu složitejší. Při objednávání obědů se využívá cookies. Uživatel si vybere jaké obědy chce přihlásit. Každé přihlášení je POST request. Uživatel pošle konkrétní oběd. Server mu vrátí upravené cookies. Uživatel může přihlásit další obědy nebo klikne uložit objednávky. Poté se pošle cookies na server a server to zpracuje a přihlásí.
