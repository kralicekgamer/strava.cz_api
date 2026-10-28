import unicodedata
from functools import lru_cache

from ._http import check_lang, shared_transport
from .models import days_from_menu

CANTEEN_FIELDS = (
    "V_NAZEV,V_ULICE,V_MESTO,V_PSC,V_TELEFON,V_UCET,V_EMAIL,V_URL,DATCAS_AKT,"
    "VERZE,URLWSDL_S-URL,GPSDELKA,GPSSIRKA,IGN_CERT,TEXT_ANON,LOGO"
)


def canteen_number(cislo):
    """Číslo jídelny jako string – `42` -> `"0042"`, `"0000"` zůstane."""
    if isinstance(cislo, int):
        return str(cislo).zfill(4)
    return str(cislo).strip()


def _first(data, key, default=None):
    value = data.get(key)
    if isinstance(value, list):
        return value[0] if value else default
    return value if value is not None else default


def _fold(text):
    text = unicodedata.normalize("NFKD", str(text or ""))
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


@lru_cache(maxsize=256)
def _canteen_cached(cislo):
    return shared_transport().post("s4Polozky", {"cislo": cislo, "lang": "CZ", "polozky": CANTEEN_FIELDS})


class Public:
    """Veřejné endpointy – nevyžadují přihlášení."""

    @staticmethod
    def canteens():
        """
        Seznam všech jídelen (`zarAMesta`).

        :return: list[dict] – položky `zarizeni`, `v_nazev`, `v_ulice`, `v_mesto` (hodnoty jsou listy)
        """
        return shared_transport().post("zarAMesta", {"lang": "CZ"})

    @staticmethod
    def search_canteens(text):
        """
        Vyhledá jídelny podle čísla, názvu, ulice nebo města (bez ohledu na diakritiku a velikost písmen).

        :return: list[dict] – `{"number", "name", "street", "city"}`
        """
        needle = _fold(text)
        result = []
        for item in Public.canteens():
            row = {
                "number": _first(item, "zarizeni", ""),
                "name": _first(item, "v_nazev", ""),
                "street": _first(item, "v_ulice", ""),
                "city": _first(item, "v_mesto", ""),
            }
            if needle in _fold(" ".join(row.values())):
                result.append(row)
        return result

    @staticmethod
    def canteen(cislo):
        """
        Informace o jídelně (`s4Polozky`) – název, adresa, kontakt, verze, s5url… Výsledek se cachuje.

        :return: dict (hodnoty jsou listy, např. `{"v_nazev": ["…"]}`)
        """
        return _canteen_cached(canteen_number(cislo))

    @staticmethod
    def s5url(cislo):
        """URL webové služby jídelny (`urlwsdl_s`). U S4 jídelen bývá prázdná."""
        return _first(Public.canteen(cislo), "urlwsdl_s", "") or ""

    @staticmethod
    def version(cislo):
        """Verze softwaru jídelny, např. `"5.14"`."""
        return _first(Public.canteen(cislo), "verze")

    @staticmethod
    def ignore_cert(cislo):
        return _first(Public.canteen(cislo), "ign_cert") == "A"

    @staticmethod
    def version_info(cislo, lang="CZ"):
        """
        Verze S5 a čas poslední aktualizace dat jídelny (`verzeS5`). Jen pro S5 jídelny.

        :return: dict
        """
        cislo = canteen_number(cislo)
        return shared_transport().post("verzeS5", {
            "cislo": cislo,
            "url": Public.s5url(cislo),
            "lang": check_lang(lang),
            "ignoreCert": Public.ignore_cert(cislo),
            "getLastActualization": True,
        })

    @staticmethod
    def menu(cislo, lang="CZ"):
        """
        Veřejný jídelníček (`jidelnicky`).

        :return: list[dict] – `[{"table0": [...], "table1": [...]}]`
        """
        cislo = canteen_number(cislo)
        return shared_transport().post("jidelnicky", {
            "cislo": cislo,
            "s5url": Public.s5url(cislo),
            "lang": check_lang(lang),
            "ignoreCert": Public.ignore_cert(cislo),
        })

    @staticmethod
    def menu_days(cislo, lang="CZ"):
        """Veřejný jídelníček rozdělený na dny. :return: list[MenuDay]"""
        return days_from_menu(Public.menu(cislo, lang))

    @staticmethod
    def menu_page(cislo, lang="CZ"):
        """
        Data veřejné stránky jídelníčku (`jidelnickyPage`) – jídelna i jídla v jednom requestu.

        :return: dict – `{"canteen": {...}, "meals": {"table0": [...]}, "objednavkyOdDo": ...}`
        """
        return shared_transport().post("jidelnickyPage", {"cislo": canteen_number(cislo), "lang": check_lang(lang)})

    @staticmethod
    def clear_cache():
        """Smaže cache `canteen()`."""
        _canteen_cached.cache_clear()
