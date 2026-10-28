"""Zpětná kompatibilita s 2.x – nový klient je `strava_cz_api.Strava`."""
from .legacy import Api, Auth, Public  # noqa: F401
