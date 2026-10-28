import unittest
import warnings
from datetime import date, datetime, timedelta
from unittest import mock

from strava_cz_api import (
    Api, AuthError, ChybnyUzivatel, Meal, Public, SessionExpiredError, Strava, StravaError,
    UserBlockedError, days_from_menu,
)
from strava_cz_api.errors import ApiError, raise_api_error
from strava_cz_api.legacy import Auth

FUTURE = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT11:50:00")
PAST = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT11:50:00")

MEAL = {
    "id": 0, "datum": "30.06.2026", "druh_popis": "Polévka", "druh_chod": "Oběd", "nazev": "Oběd 1",
    "popis": "", "delsiPopis": "", "alergeny": [["01", "Obiloviny  "], "07"], "chod": "C", "druh": "OB",
    "cena": "45.00", "polevka": "N", "pocet": 0, "veta": "172", "cisloJidelnicku": "1",
    "omezeniObj": {"den": "", "obj": "", "zm": "", "bur": "C"},
    "vydejniMisto": {"misto": "2", "mista": "2"}, "diety": {"dieta": "", "diety": ""},
    "casKonec": FUTURE, "casOdhlaseni": FUTURE, "obrazky": [],
}
MENU = {
    "table0": [MEAL, dict(MEAL, veta="173", pocet=1, nazev="Oběd 2")],
    "table1": [dict(MEAL, datum="01.07.2026", veta="180")],
}


class FakeTransport:
    def __init__(self, responses=None):
        self.calls = []
        self.responses = responses or {}

    def post(self, endpoint, payload):
        self.calls.append((endpoint, payload))
        response = self.responses.get(endpoint, {})
        if isinstance(response, Exception):
            raise response
        if callable(response):
            return response(payload)
        return response

    def close(self):
        pass

    def seed_cookie(self, cookie):
        pass


def client(**responses):
    transport = FakeTransport(responses)
    strava = Strava("SID", "0000", "S5URL", user={"id": "jan", "evCislo": "77"}, transport=transport)
    return strava, transport


class PayloadTests(unittest.TestCase):
    def check(self, call, endpoint, **expected):
        strava, transport = client(objednavky=MENU, messagesGetAmount={"values": {"JidelnaNeprectene": 2, "MarketingNeprectene": 1}})
        call(strava)
        sent_endpoint, payload = transport.calls[-1]
        self.assertEqual(sent_endpoint, endpoint)
        for key, value in expected.items():
            self.assertEqual(payload.get(key), value, f"{endpoint}.{key}")
        return payload

    def test_menu_uses_s5url_key(self):
        payload = self.check(lambda s: s.menu(), "objednavky", cislo="0000", sid="SID", s5url="S5URL", konto=0)
        self.assertNotIn("url", payload)

    def test_order_and_cancel(self):
        self.check(lambda s: s.order("172"), "pridejJidloS5", veta="172", pocet=1, url="S5URL")
        self.check(lambda s: s.cancel(Meal.from_dict(MEAL)), "pridejJidloS5", veta="172", pocet=0)

    def test_day(self):
        self.check(lambda s: s.order_day("30.12.2025"), "objednejDenS5", datum="2025-12-30", pocet=1)
        self.check(lambda s: s.cancel_day(date(2025, 12, 30)), "objednejDenS5", datum="2025-12-30", pocet=0)

    def test_simple_endpoints(self):
        self.check(lambda s: s.save_orders(), "saveOrders", xml=None)
        self.check(lambda s: s.discard_changes(), "resetTabulekS5", sid="SID")
        self.check(lambda s: s.change_pickup_place("172", "3"), "zmenVydejniMisto", veta="172", vydejniMisto="3")
        self.check(lambda s: s.change_diet("172", "B"), "zmenDietu", veta="172", dieta="B")
        self.check(lambda s: s.user_info(), "userInfo", s5url="S5URL")
        self.check(lambda s: s.properties(), "nactiVlastnostiPA", resetTables=False, frontendFunction="refreshInformations")
        self.check(lambda s: s.history("2025-03-17"), "historieKlienta", datum="2025-03-01")
        self.check(lambda s: s.payments(), "platby")
        self.check(lambda s: s.payment_qr(), "qr")
        self.check(lambda s: s.issued_meals(), "vydej", s5url="S5URL")
        self.check(lambda s: s.protocol(), "getProtokol", uroven="KP", evCislo=0)
        self.check(lambda s: s.enrollment_form(), "nactiZapisovyListek")
        self.check(lambda s: s.logout(), "logOut", sid="SID", url="S5URL")
        payload = self.check(lambda s: s.canteen(), "jidelnaS5", url="S5URL")
        self.assertNotIn("sid", payload)

    def test_attendance_defaults_to_whole_month(self):
        payload = self.check(lambda s: s.attendance("2024-02-01", bakalar_id="B1"), "attendance", id="B1")
        self.assertEqual(payload["dateTo"], "2024-02-29")

    def test_messages(self):
        self.check(lambda s: s.messages(), "messagesGetList", idJ="0000", idU="jan", typZpravy="")
        self.check(lambda s: s.message(5), "messagesGetDetail", idZ=5)
        payload = self.check(lambda s: s.mark_read(1, 2), "messagesSetRead", idU="jan")
        self.assertEqual([z["IDZpravy"] for z in payload["zpravy"]], [1, 2])
        strava, _ = client(messagesGetAmount={"values": {"JidelnaNeprectene": 2, "MarketingNeprectene": 1}})
        self.assertEqual(strava.unread_count(), 3)

    def test_meal_details_and_rating(self):
        meal = Meal.from_dict(MEAL)
        self.check(lambda s: s.meal_details(meal), "orderModalDetails", veta="172", datum="2026-06-30", druh="OB", cisloJidelnicku="1")
        payload = self.check(lambda s: s.rate_meal(meal, 5), "zapisHodnoceniJidel")
        xml = payload["xmlHodnoceni"]
        for part in ('EvCislo="77"', 'Datum="20260630"', 'Druh="OB"', 'CisloJidelnicku="1"', 'Hodnoceni="5"'):
            self.assertIn(part, xml)

    def test_set_language(self):
        strava, transport = client()
        strava.set_language("en")
        self.assertEqual(transport.calls[-1][1]["lang"], "EN")
        self.assertEqual(strava.lang, "EN")
        with self.assertRaises(ValueError):
            strava.set_language("DE")

    def test_balance(self):
        strava, _ = client(nactiVlastnostiPA={"id": "jan", "uzivatel": {"konto": "123.50"}})
        self.assertEqual(strava.balance(), 123.5)


class MenuTests(unittest.TestCase):
    def test_meals_and_days(self):
        strava, _ = client(objednavky=MENU)
        self.assertEqual(len(strava.meals()), 3)
        self.assertEqual([d.date for d in strava.days()], [date(2026, 6, 30), date(2026, 7, 1)])
        self.assertEqual([m.veta for m in strava.ordered_meals()], ["173"])
        self.assertEqual([m.veta for m in strava.menu_for("2026-07-01")], ["180"])

    def test_meal_model(self):
        meal = Meal.from_dict(MEAL)
        self.assertEqual(meal.date, date(2026, 6, 30))
        self.assertEqual(meal.price, 45.0)
        self.assertEqual(meal.allergens, [("01", "Obiloviny"), ("07", "")])
        self.assertEqual(meal.pickup_place, "2")
        self.assertFalse(meal.ordered)
        self.assertTrue(meal.can_order)
        self.assertFalse(meal.can_cancel)

    def test_meal_locks(self):
        self.assertFalse(Meal.from_dict(dict(MEAL, omezeniObj={"obj": "C"})).can_order)
        self.assertFalse(Meal.from_dict(dict(MEAL, casKonec=PAST)).can_order)
        self.assertTrue(Meal.from_dict(dict(MEAL, pocet=1)).can_cancel)
        self.assertFalse(Meal.from_dict(dict(MEAL, pocet=1, omezeniObj={"zm": "I"})).can_cancel)
        self.assertFalse(Meal.from_dict(dict(MEAL, veta=None)).can_order)

    def test_tolerates_missing_keys(self):
        meal = Meal.from_dict({"nazev": "x"})
        self.assertIsNone(meal.date)
        self.assertIsNone(meal.price)

    def test_public_list_shape(self):
        self.assertEqual(len(days_from_menu([MENU])), 2)

    def test_ics(self):
        strava, _ = client(objednavky=MENU)
        ics = strava.export_ics()
        self.assertTrue(ics.startswith("BEGIN:VCALENDAR"))
        self.assertEqual(ics.count("BEGIN:VEVENT"), 1)
        self.assertIn("DTSTART;VALUE=DATE:20260630", ics)


class ErrorTests(unittest.TestCase):
    def test_mapping(self):
        with self.assertRaises(ChybnyUzivatel) as ctx:
            raise_api_error({"state": "error", "number": 13404, "message": "Chybný uživatel"})
        self.assertEqual(ctx.exception.number, 13404)
        self.assertEqual(ctx.exception.message, "Chybný uživatel")
        with self.assertRaises(AuthError):
            raise_api_error({"state": "error", "number": "10102"})
        with self.assertRaises(SessionExpiredError):
            raise_api_error({"state": "error", "number": 10102})
        with self.assertRaises(UserBlockedError):
            raise_api_error({"state": "error", "number": 20})
        with self.assertRaises(ApiError):
            raise_api_error({"state": "error", "number": 4242})
        with self.assertRaises(StravaError):
            raise_api_error({"state": "error", "number": 3})
        self.assertIsNone(raise_api_error({"state": "success"}))

    def test_auto_relogin(self):
        attempts = {"n": 0}

        def menu(payload):
            attempts["n"] += 1
            if payload["sid"] == "OLD":
                raise AuthError("expired", number=10102)
            return MENU

        transport = FakeTransport({"objednavky": menu, "login": {"sid": "NEW", "s5url": "S5URL", "uzivatel": {"id": "jan"}}})
        strava = Strava("OLD", "0000", "S5URL", transport=transport)
        strava._credentials = ("jan", "heslo", True)
        self.assertEqual(strava.menu(), MENU)
        self.assertEqual(strava.sid, "NEW")
        self.assertEqual(attempts["n"], 2)

    def test_no_relogin_without_credentials(self):
        strava, _ = client(objednavky=AuthError("expired", number=10102))
        with self.assertRaises(AuthError):
            strava.menu()


class LoginTests(unittest.TestCase):
    def test_login_builds_client(self):
        response = {"sid": "S", "s5url": "U", "cislo": "0000", "ignoreCert": "false", "uzivatel": {"id": "jan", "evCislo": "7"}}
        with mock.patch("strava_cz_api.client.Transport", return_value=FakeTransport({"login": response})):
            strava = Strava.login("jan", "heslo", 0)
        login_call = strava.transport.calls[0]
        self.assertEqual(login_call[0], "login")
        self.assertEqual(login_call[1]["cislo"], "0000")
        self.assertEqual((strava.sid, strava.s5url, strava.username), ("S", "U", "jan"))

    def test_context_manager_logs_out(self):
        strava, transport = client()
        with strava:
            pass
        self.assertEqual(transport.calls[-1][0], "logOut")


class LegacyTests(unittest.TestCase):
    def legacy(self):
        transport = FakeTransport({"objednavky": MENU})
        with mock.patch("strava_cz_api.client.Transport", return_value=transport):
            api = Api("SID", "S5URL", "0000", cookie="a=1")
        return api, transport

    def test_aliases_warn_and_call_new_endpoints(self):
        api, transport = self.legacy()
        cases = [
            (lambda: api.getJidelnicekAll(), "objednavky"),
            (lambda: api.postJidlo("172", 1), "pridejJidloS5"),
            (lambda: api.postDen("2025-12-30", 0), "objednejDenS5"),
            (lambda: api.postOrders(), "saveOrders"),
            (lambda: api.getPlatby(), "platby"),
            (lambda: api.getVydej(), "vydej"),
            (lambda: api.getProtokol(), "getProtokol"),
            (lambda: api.getHistorieKlienta("2025-01-01"), "historieKlienta"),
            (lambda: api.resetChanges(), "nactiVlastnostiPA"),
            (lambda: api.logOut(), "logOut"),
        ]
        for call, endpoint in cases:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                call()
            self.assertTrue(any(issubclass(w.category, DeprecationWarning) for w in caught), endpoint)
            self.assertEqual(transport.calls[-1][0], endpoint)

    def test_today_keeps_table0(self):
        api, _ = self.legacy()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(api.getJidelnicekToday(), MENU["table0"])
        self.assertEqual(api.cislo_jidelny, "0000")

    def test_get_credentials(self):
        self.assertEqual(Auth.getCredentials('{"sid": "S", "s5url": "U"}'), ("S", "U"))

    def test_public_aliases(self):
        with mock.patch("strava_cz_api.public._canteen_cached", return_value={"verze": ["5.14"], "urlwsdl_s": ["X"]}):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.assertEqual(Public.getVersion("0000"), "5.14")
                self.assertEqual(Public.getS5url("0000"), "X")


if __name__ == "__main__":
    unittest.main()
