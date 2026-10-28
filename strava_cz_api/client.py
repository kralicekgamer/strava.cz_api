from datetime import date, datetime, timedelta, timezone
from functools import cached_property

from ._http import DEFAULT_TIMEOUT, Transport, check_lang
from .errors import SessionExpiredError
from .models import Meal, days_from_menu, meals_from_menu, parse_date, to_iso
from .public import canteen_number


def _find_key(data, key):
    """První hodnota klíče `key` kdekoli ve vnořeném dict/list."""
    if isinstance(data, dict):
        if key in data:
            return data[key]
        values = data.values()
    elif isinstance(data, list):
        values = data
    else:
        return None
    for value in values:
        found = _find_key(value, key)
        if found is not None:
            return found
    return None


def _prague_now():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Europe/Prague"))
    except Exception:
        return datetime.now()


class Strava:
    """
    Přihlášený klient pro app.strava.cz.

    Nejjednodušší je vytvořit ho přes `Strava.login(...)`. Pokud už máš SID,
    můžeš ho vytvořit přímo: `Strava(sid, canteen, s5url)`.
    """

    def __init__(self, sid, canteen, s5url="", lang="CZ", ignore_cert="false", user=None,
                 timeout=DEFAULT_TIMEOUT, transport=None):
        self.sid = sid
        self.canteen_number = canteen_number(canteen)
        self.s5url = s5url or ""
        self.lang = check_lang(lang)
        self.ignore_cert = ignore_cert
        self.user = user or {}
        self.transport = transport or Transport(timeout=timeout)
        self.login_data = None
        self._credentials = None

    # ------------------------------------------------------------------ session

    @classmethod
    def login(cls, username, password, canteen, lang="CZ", remember=True, auto_relogin=False,
              timeout=DEFAULT_TIMEOUT):
        """
        Přihlásí uživatele a vrátí připravený klient.

        :param remember: odpovídá zaškrtávátku "Zůstat přihlášen"
        :param auto_relogin: při vypršení SID se klient jednou sám znovu přihlásí (drží heslo v paměti)
        :return: Strava
        """
        transport = Transport(timeout=timeout)
        lang = check_lang(lang)
        cislo = canteen_number(canteen)
        data = cls._login_request(transport, username, password, cislo, lang, remember)
        client = cls(
            sid=data.get("sid"),
            canteen=data.get("cislo") or cislo,
            s5url=data.get("s5url"),
            lang=lang,
            ignore_cert=data.get("ignoreCert", "false"),
            user=data.get("uzivatel") or {},
            transport=transport,
        )
        client.login_data = data
        if auto_relogin:
            client._credentials = (username, password, remember)
        return client

    @staticmethod
    def _login_request(transport, username, password, cislo, lang, remember):
        return transport.post("login", {
            "cislo": cislo,
            "jmeno": username,
            "heslo": password,
            "zustatPrihlasen": remember,
            "environment": "W",
            "lang": lang,
        })

    def relogin(self):
        """Znovu se přihlásí uloženými údaji (jen s `auto_relogin=True`)."""
        if not self._credentials:
            raise SessionExpiredError("Nelze se znovu přihlásit – klient nebyl vytvořen s auto_relogin=True.")
        username, password, remember = self._credentials
        data = self._login_request(self.transport, username, password, self.canteen_number, self.lang, remember)
        self.sid = data.get("sid")
        self.s5url = data.get("s5url") or ""
        self.ignore_cert = data.get("ignoreCert", self.ignore_cert)
        self.user = data.get("uzivatel") or self.user
        self.__dict__.pop("username", None)
        return data

    def logout(self):
        """Odhlásí uživatele (`logOut`). SID poté přestane platit."""
        return self._call("logOut", self._payload(), retry=False)

    def close(self):
        self.transport.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        try:
            self.logout()
        except Exception:
            pass
        self.close()
        return False

    def __repr__(self):
        return f"<Strava canteen={self.canteen_number!r} user={self.user.get('id')!r}>"

    # ------------------------------------------------------------------ helpers

    def _payload(self, url_key="url", sid=True, **extra):
        payload = {"cislo": self.canteen_number, url_key: self.s5url, "lang": self.lang, "ignoreCert": self.ignore_cert}
        if sid:
            payload["sid"] = self.sid
        payload.update(extra)
        return payload

    def _call(self, endpoint, payload, retry=True):
        try:
            return self.transport.post(endpoint, payload)
        except SessionExpiredError:
            if not (retry and self._credentials):
                raise
            old_sid = self.sid
            self.relogin()
            if payload.get("sid") == old_sid:
                payload = dict(payload, sid=self.sid)
            return self.transport.post(endpoint, payload)

    def _messages_payload(self, **extra):
        payload = {"sid": "", "idO": "", "idJ": self.canteen_number, "idU": self.username}
        payload.update(extra)
        return payload

    @staticmethod
    def _veta(meal):
        if isinstance(meal, Meal):
            return meal.veta
        if isinstance(meal, dict):
            return meal.get("veta")
        return str(meal)

    # ------------------------------------------------------------------ jídelníček

    def menu(self):
        """
        Celý jídelníček s objednávkami (`objednavky`).

        :return: dict – `{"table0": [...], "table1": [...]}`, každá tabulka = jeden den
        """
        return self._call("objednavky", self._payload("s5url", konto=0, podminka=""))

    def days(self):
        """Jídelníček rozdělený na dny. :return: list[MenuDay]"""
        return days_from_menu(self.menu())

    def meals(self):
        """Všechna jídla jako objekty. :return: list[Meal]"""
        return meals_from_menu(self.menu())

    def menu_for(self, day):
        """
        Jídla na konkrétní den.

        :param day: `date`, `"2025-12-30"` nebo `"30.12.2025"`
        :return: list[Meal]
        """
        wanted = parse_date(day)
        return [meal for meal in self.meals() if meal.date == wanted]

    def menu_today(self):
        """Dnešní jídla. :return: list[Meal]"""
        return self.menu_for(date.today())

    def ordered_meals(self):
        """Objednaná (přihlášená) jídla. :return: list[Meal]"""
        return [meal for meal in self.meals() if meal.ordered]

    def meal_details(self, meal, weights=True, rating=True):
        """
        Detail jídla (`orderModalDetails`) – gramáže, nutriční hodnoty, hodnocení.

        :param meal: `Meal` nebo dict z `menu()`
        :return: dict
        """
        raw = meal.raw if isinstance(meal, Meal) else meal
        return self._call("orderModalDetails", self._payload(
            veta=raw.get("veta"),
            cisloJidelnicku=raw.get("cisloJidelnicku"),
            datum=to_iso(raw.get("datum")),
            druh=raw.get("druh"),
            fetchGramaze=weights,
            fetchHodnoceni=rating,
        ))

    # ------------------------------------------------------------------ objednávky

    def set_meal_count(self, meal, count):
        """
        Nastaví počet kusů jídla (`pridejJidloS5`). 0 = odhlásit, 1 = přihlásit.
        Změna se projeví až po `save_orders()`.

        :param meal: `veta`, `Meal` nebo dict
        """
        return self._call("pridejJidloS5", self._payload(veta=self._veta(meal), pocet=int(count)))

    def order(self, meal):
        """Přihlásí jídlo. Nezapomeň potom zavolat `save_orders()`."""
        return self.set_meal_count(meal, 1)

    def cancel(self, meal):
        """Odhlásí jídlo. Nezapomeň potom zavolat `save_orders()`."""
        return self.set_meal_count(meal, 0)

    def set_day(self, day, count):
        """Přihlásí (1) / odhlásí (0) celý den (`objednejDenS5`). Uložit přes `save_orders()`."""
        return self._call("objednejDenS5", self._payload(datum=to_iso(day), pocet=int(count)))

    def order_day(self, day):
        """Přihlásí celý den."""
        return self.set_day(day, 1)

    def cancel_day(self, day):
        """Odhlásí celý den."""
        return self.set_day(day, 0)

    def change_pickup_place(self, meal, place):
        """Změní výdejní místo jídla (`zmenVydejniMisto`). Uložit přes `save_orders()`."""
        return self._call("zmenVydejniMisto", self._payload(veta=self._veta(meal), vydejniMisto=place))

    def change_diet(self, meal, diet):
        """Změní dietu u jídla (`zmenDietu`). Uložit přes `save_orders()`."""
        return self._call("zmenDietu", self._payload(veta=self._veta(meal), dieta=diet))

    def save_orders(self):
        """
        Uloží všechny neuložené změny objednávek (`saveOrders`). Funguje pro S5 jídelny.

        :return: dict – obsahuje mimo jiné nový stav konta
        """
        return self._call("saveOrders", self._payload(xml=None))

    def discard_changes(self):
        """Zahodí neuložené změny objednávek a znovu načte data (`resetTabulekS5`)."""
        return self._call("resetTabulekS5", self._payload())

    def rate_meal(self, meal, rating, note=""):
        """
        Ohodnotí jídlo (`zapisHodnoceniJidel`).

        :param meal: `Meal` nebo dict z `menu()`
        :param rating: hodnocení (číslo, stejné jako hvězdičky na webu)
        """
        raw = meal.raw if isinstance(meal, Meal) else meal
        ev_cislo = self.user.get("evCislo", "")
        xml = (
            '<?xml version="1.0" encoding="utf-8"?><HodnoceniJidel>'
            f'<HodnoceniJidla EvCislo="{ev_cislo}" Datum="{to_iso(raw.get("datum")).replace("-", "")}" '
            f'Druh="{raw.get("druh", "")}" CisloJidelnicku="{raw.get("cisloJidelnicku", "")}" '
            f'Hodnoceni="{rating}" Poznamka="{_xml_escape(note)}" '
            f'DatumAktualizace="{_prague_now().strftime("%Y%m%d%H%M%S")}" /></HodnoceniJidel>'
        )
        return self._call("zapisHodnoceniJidel", self._payload(xmlHodnoceni=xml))

    # ------------------------------------------------------------------ účet

    def user_info(self):
        """Veškeré informace o uživateli (`userInfo`) – osobní údaje, nastavení, e-mail…"""
        return self._call("userInfo", self._payload("s5url"))

    def properties(self, reset_tables=False):
        """
        Vlastnosti uživatele a jídelny (`nactiVlastnostiPA`).

        :param reset_tables: True = Strava znovu načte tabulky (trvá dlouho)
        """
        return self._call("nactiVlastnostiPA", self._payload(
            getText=True,
            checkVersion=True,
            resetTables=reset_tables,
            frontendFunction="refreshInformations",
        ))

    @cached_property
    def username(self):
        """Uživatelské jméno (ID strávníka). Bere se z přihlášení, jinak z `properties()`."""
        return self.user.get("id") or self.properties().get("id")

    def balance(self):
        """
        Aktuální stav konta v Kč.

        :return: float | None
        """
        value = _find_key(self.properties(), "konto")
        if value is None:
            value = self.user.get("konto")
        try:
            return float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return None

    def history(self, month=None):
        """
        Historie objednávek a pohybů na kontě za měsíc (`historieKlienta`).

        :param month: libovolný den v měsíci (`date` nebo string); výchozí je aktuální měsíc
        """
        first = (parse_date(month) if month else date.today()).replace(day=1)
        return self._call("historieKlienta", self._payload(datum=first.isoformat()))

    def payments(self):
        """Platby a pohyby na účtu (`platby`)."""
        return self._call("platby", self._payload())

    def payment_qr(self):
        """Údaje pro dobití konta – číslo účtu, VS… (`qr`). Jen S5 jídelny."""
        return self._call("qr", self._payload())

    def issued_meals(self):
        """Vydaná jídla (`vydej`)."""
        return self._call("vydej", self._payload("s5url"))

    def protocol(self):
        """Protokol změn (`getProtokol`). Jen S5 jídelny."""
        return self._call("getProtokol", self._payload("s5url", uroven="KP", evCislo=0))

    def enrollment_form(self):
        """Přihláška ke stravování / zápisový lístek (`nactiZapisovyListek`)."""
        return self._call("nactiZapisovyListek", self._payload())

    def attendance(self, date_from=None, date_to=None, bakalar_id=None):
        """
        Docházka z Bakalářů (`attendance`). Funguje jen u jídelen propojených s Bakaláři.

        :param date_from: výchozí je první den aktuálního měsíce
        :param date_to: výchozí je poslední den aktuálního měsíce
        :param bakalar_id: ID z Bakalářů; výchozí je `user["bakalarId"]`
        """
        today = date.today()
        start = parse_date(date_from) if date_from else today.replace(day=1)
        end = parse_date(date_to) if date_to else (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return self._call("attendance", {
            "id": bakalar_id or self.user.get("bakalarId", ""),
            "cislo": self.canteen_number,
            "dateFrom": start.isoformat(),
            "dateTo": end.isoformat(),
            "lang": self.lang,
        })

    def set_language(self, lang):
        """Změní jazyk na straně Stravy (`zmenJazyk`, S5 >= 5.13) i v klientovi."""
        lang = check_lang(lang)
        data = self._call("zmenJazyk", self._payload(lang=lang))
        self.lang = lang
        return data

    def canteen(self):
        """Informace o jídelně z S5 (`jidelnaS5`)."""
        return self._call("jidelnaS5", self._payload(sid=False))

    # ------------------------------------------------------------------ zprávy

    def messages(self, message_type=""):
        """Seznam zpráv pro uživatele (`messagesGetList`)."""
        return self._call("messagesGetList", self._messages_payload(typZpravy=message_type))

    def unread_count(self):
        """
        Počet nepřečtených zpráv (`messagesGetAmount`).

        :return: int
        """
        values = self._call("messagesGetAmount", self._messages_payload()).get("values") or {}
        return int(values.get("JidelnaNeprectene") or 0) + int(values.get("MarketingNeprectene") or 0)

    def message(self, message_id):
        """Detail (text) jedné zprávy (`messagesGetDetail`)."""
        return self._call("messagesGetDetail", {"idZ": message_id})

    def mark_read(self, *message_ids):
        """Označí zprávy jako přečtené (`messagesSetRead`)."""
        zpravy = [{"IDZpravy": message_id, "StavZpravy": "Přečteno"} for message_id in message_ids]
        return self._call("messagesSetRead", self._messages_payload(zpravy=zpravy))

    def confirm_notice(self):
        """Potvrdí upozornění od jídelny (`potvrdUpozorneni`)."""
        return self._call("potvrdUpozorneni", self._payload())

    # ------------------------------------------------------------------ extra

    def export_ics(self, path=None, only_ordered=True):
        """
        Vyexportuje jídla do kalendáře (iCalendar / .ics).

        :param path: když je zadaná, soubor se rovnou uloží
        :param only_ordered: False = exportuje celý jídelníček
        :return: str – obsah .ics
        """
        meals = self.ordered_meals() if only_ordered else self.meals()
        return meals_to_ics(meals, path, uid_prefix=self.canteen_number)


def _xml_escape(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def _ics_escape(text):
    return str(text).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def meals_to_ics(meals, path=None, uid_prefix="strava"):
    """Převede list `Meal` na iCalendar (celodenní události)."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//strava-cz-api//CS", "CALSCALE:GREGORIAN"]
    for meal in meals:
        if meal.date is None:
            continue
        title = f"{meal.meal_type or meal.course}: {meal.name}".strip(": ")
        details = [meal.course, f"Cena: {meal.price:.2f} Kč" if meal.price is not None else ""]
        if meal.allergens:
            details.append("Alergeny: " + ", ".join(code for code, _ in meal.allergens))
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid_prefix}-{meal.date:%Y%m%d}-{meal.veta or meal.raw.get('id')}@strava-cz-api",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{meal.date:%Y%m%d}",
            f"DTEND;VALUE=DATE:{meal.date + timedelta(days=1):%Y%m%d}",
            f"SUMMARY:{_ics_escape(title)}",
            f"DESCRIPTION:{_ics_escape(chr(10).join(d for d in details if d))}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    content = "\r\n".join(lines) + "\r\n"
    if path:
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
    return content
