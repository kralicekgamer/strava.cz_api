class StravaError(Exception):
    """Základní výjimka. Obsahuje číslo chyby (`number`) a zprávu ze Stravy (`message`)."""

    def __init__(self, message="", number=None, response=None):
        self.number = number
        self.message = message
        self.response = response
        if number is None:
            super().__init__(message)
        else:
            super().__init__(f"\n\n---=== Error: #{number} ===---\n{message}\n    ")


class StravaConnectionError(StravaError):
    """Síťová chyba – server neodpověděl, timeout spojení, DNS…"""


class SessionExpiredError(StravaError):
    """SID je neplatné nebo vypršelo, je potřeba se znovu přihlásit."""


class JidelnaNenalezenaError(StravaError):
    pass

class ChybneHesloError(StravaError):
    pass

class BackendError(StravaError):
    pass

class ChybneSID(SessionExpiredError):
    pass

class ChybnyUzivatel(StravaError):
    pass

class NelzePrihlasit(StravaError):
    pass

class NelzeVytvoritSID(StravaError):
    pass

class AuthError(SessionExpiredError):
    pass

class S5Payload(StravaError):
    pass

class S5AndJidelnaPayload(StravaError):
    pass

class ApiError(StravaError):
    pass

class Timeout(StravaError):
    pass

class LoginTimeout(StravaError):
    pass

class UserBlockedError(StravaError):
    """Strávník je na jídelně zablokován a nemá práva objednávat."""


ERROR_MAP = {
    6: JidelnaNenalezenaError,
    13: SessionExpiredError,
    14: NelzeVytvoritSID,
    15: ChybneSID,
    20: UserBlockedError,
    30: S5AndJidelnaPayload,
    35: NelzePrihlasit,
    90: SessionExpiredError,
    998: Timeout,
    1009: SessionExpiredError,
    1010: SessionExpiredError,
    1011: SessionExpiredError,
    1014: SessionExpiredError,
    3002: BackendError,
    10102: AuthError,
    10104: SessionExpiredError,
    13201: S5Payload,
    13404: ChybnyUzivatel,
    13405: ChybneHesloError,
    13410: LoginTimeout,
    "99+": ApiError,
}


def _to_int(number):
    try:
        return int(number)
    except (TypeError, ValueError):
        return number


def raise_api_error(data):
    """Vyhodí odpovídající výjimku, pokud odpověď Stravy obsahuje `state: error`."""
    if not isinstance(data, dict) or data.get("state") != "error":
        return

    number = _to_int(data.get("number"))
    message = data.get("message", "Neznámá chyba")

    exc = ERROR_MAP.get(number)
    if exc is None:
        exc = ApiError if isinstance(number, int) and number >= 99 else StravaError
    raise exc(message, number=number, response=data)
