from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Tuple

# Písmena v `omezeniObj`, která znamenají, že s jídlem nejde hýbat:
# C – nelze objednat/změnit, I – vždy přihlášeno (polévka), V – svátek.
_LOCKED = ("C", "I", "V")


def parse_date(value) -> Optional[date]:
    """Převede `30.06.2026`, `2026-06-30` nebo `date`/`datetime` na `date`."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    return None


def parse_datetime(value) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def to_iso(value) -> str:
    """Datum pro payload Stravy (`YYYY-MM-DD`)."""
    parsed = parse_date(value)
    if parsed is None:
        raise ValueError(f"Neplatné datum: {value!r} (očekávám YYYY-MM-DD, DD.MM.YYYY nebo date)")
    return parsed.isoformat()


def _float(value) -> Optional[float]:
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _int(value, default=0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _allergens(value) -> List[Tuple[str, str]]:
    result = []
    for item in value or []:
        if isinstance(item, (list, tuple)) and item:
            code = str(item[0]).strip()
            name = str(item[1]).strip() if len(item) > 1 else ""
            result.append((code, name))
        elif item not in (None, ""):
            result.append((str(item).strip(), ""))
    return result


@dataclass(frozen=True)
class Meal:
    """Jedno jídlo z jídelníčku. Originální data jsou v `raw`."""

    veta: Optional[str]
    date: Optional[date]
    name: str
    description: str
    course: str
    meal_type: str
    chod: str
    druh: str
    menu_number: Optional[str]
    price: Optional[float]
    count: int
    is_soup: bool
    allergens: List[Tuple[str, str]]
    restrictions: dict
    order_deadline: Optional[datetime]
    cancel_deadline: Optional[datetime]
    pickup_place: Optional[str]
    diet: Optional[str]
    images: List[str]
    raw: dict = field(repr=False, compare=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Meal":
        veta = data.get("veta")
        return cls(
            veta=str(veta) if veta not in (None, "") else None,
            date=parse_date(data.get("datum")),
            name=(data.get("nazev") or "").strip(),
            description=(data.get("delsiPopis") or data.get("popis") or "").strip(),
            course=(data.get("druh_popis") or "").strip(),
            meal_type=(data.get("druh_chod") or "").strip(),
            chod=data.get("chod") or "",
            druh=data.get("druh") or "",
            menu_number=data.get("cisloJidelnicku"),
            price=_float(data.get("cena")),
            count=_int(data.get("pocet")),
            is_soup=data.get("polevka") == "A",
            allergens=_allergens(data.get("alergeny")),
            restrictions=data.get("omezeniObj") or {},
            order_deadline=parse_datetime(data.get("casKonec")),
            cancel_deadline=parse_datetime(data.get("casOdhlaseni")),
            pickup_place=(data.get("vydejniMisto") or {}).get("misto"),
            diet=(data.get("diety") or {}).get("dieta"),
            images=list(data.get("obrazky") or []),
            raw=data,
        )

    @property
    def ordered(self) -> bool:
        return self.count > 0

    def _open(self, key, deadline) -> bool:
        if not self.veta:
            return False
        if any(flag in str(self.restrictions.get(key, "")) for flag in _LOCKED):
            return False
        if deadline is not None:
            now = datetime.now(deadline.tzinfo) if deadline.tzinfo else datetime.now()
            return now < deadline
        return True

    @property
    def can_order(self) -> bool:
        """Lze jídlo teď přihlásit (podle `omezeniObj` a `casKonec`)?"""
        return not self.ordered and self._open("obj", self.order_deadline)

    @property
    def can_cancel(self) -> bool:
        """Lze jídlo teď odhlásit (podle `omezeniObj` a `casOdhlaseni`)?"""
        return self.ordered and self._open("zm", self.cancel_deadline or self.order_deadline)


@dataclass(frozen=True)
class MenuDay:
    date: Optional[date]
    meals: List[Meal]

    @property
    def ordered(self) -> List[Meal]:
        return [meal for meal in self.meals if meal.ordered]


def _tables(data):
    if isinstance(data, list):
        for item in data:
            yield from _tables(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            if key.startswith("table") and isinstance(value, list):
                yield value


def days_from_menu(data) -> List[MenuDay]:
    """Rozdělí odpověď `objednavky`/`jidelnicky` (`{"table0": [...], ...}`) na dny."""
    days = {}
    for table in _tables(data):
        for item in table:
            if isinstance(item, dict):
                meal = Meal.from_dict(item)
                days.setdefault(meal.date, []).append(meal)
    return [MenuDay(day, meals) for day, meals in sorted(days.items(), key=lambda kv: (kv[0] is None, kv[0] or date.min))]


def meals_from_menu(data) -> List[Meal]:
    return [meal for day in days_from_menu(data) for meal in day.meals]
