from .client import Strava, meals_to_ics
from .legacy import Api, Auth, Public
from .filter import Filter
from .models import Meal, MenuDay, days_from_menu, meals_from_menu
from .errors import (
    StravaError,
    StravaConnectionError,
    SessionExpiredError,
    UserBlockedError,
    JidelnaNenalezenaError,
    ChybneSID,
    NelzePrihlasit,
    NelzeVytvoritSID,
    ChybneHesloError,
    BackendError,
    ChybnyUzivatel,
    AuthError,
    S5Payload,
    S5AndJidelnaPayload,
    ApiError,
    Timeout,
    LoginTimeout,
)

__version__ = "3.0.0"

__all__ = [
    "Strava",
    "Public",
    "Filter",
    "Meal",
    "MenuDay",
    "days_from_menu",
    "meals_from_menu",
    "meals_to_ics",
    "Api",
    "Auth",
    "StravaError",
    "StravaConnectionError",
    "SessionExpiredError",
    "UserBlockedError",
    "JidelnaNenalezenaError",
    "ChybneSID",
    "NelzePrihlasit",
    "NelzeVytvoritSID",
    "ChybneHesloError",
    "BackendError",
    "ChybnyUzivatel",
    "AuthError",
    "S5Payload",
    "S5AndJidelnaPayload",
    "ApiError",
    "Timeout",
    "LoginTimeout",
]
