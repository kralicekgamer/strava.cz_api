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
