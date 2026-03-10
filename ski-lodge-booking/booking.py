"""
Ski Lodge Booking System
Manages 23 rooms with weekend (Fri/Sat nights) and weekday rates.
Data is persisted to bookings.json in the same directory.
"""

import json
import os
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Room catalogue
# ---------------------------------------------------------------------------

ROOMS: dict[int, dict] = {
    # Standard rooms (1-10)
    **{i: {"type": "Standard", "capacity": 2} for i in range(1, 11)},
    # Deluxe rooms (11-18)
    **{i: {"type": "Deluxe", "capacity": 2} for i in range(11, 19)},
    # Suite rooms (19-23)
    **{i: {"type": "Suite", "capacity": 4} for i in range(19, 24)},
}

# ---------------------------------------------------------------------------
# Rates (per night, per room)
# ---------------------------------------------------------------------------

RATES: dict[str, dict[str, float]] = {
    "Standard": {"weekday": 120.00, "weekend": 180.00},
    "Deluxe":   {"weekday": 180.00, "weekend": 260.00},
    "Suite":    {"weekday": 280.00, "weekend": 400.00},
}

WEEKEND_DAYS = {4, 5}  # Monday=0 … Friday=4, Saturday=5

# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

DATA_FILE = Path(__file__).parent / "bookings.json"


def _load() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def _save(data: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _parse_date(d: str | date) -> date:
    if isinstance(d, date):
        return d
    return date.fromisoformat(d)


def _night_dates(check_in: date, check_out: date) -> list[date]:
    """Return the list of nights (each represented by the date the guest sleeps)."""
    nights = []
    current = check_in
    while current < check_out:
        nights.append(current)
        current += timedelta(days=1)
    return nights


def _rate_for_night(night: date, room_type: str) -> float:
    kind = "weekend" if night.weekday() in WEEKEND_DAYS else "weekday"
    return RATES[room_type][kind]


def _night_label(night: date) -> str:
    kind = "weekend" if night.weekday() in WEEKEND_DAYS else "weekday"
    day_name = night.strftime("%A")
    return f"{night.isoformat()} ({day_name}, {kind})"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def list_rooms() -> list[dict]:
    """Return all 23 rooms with their type, capacity and rates."""
    result = []
    for room_num, info in ROOMS.items():
        rt = info["type"]
        result.append({
            "room": room_num,
            "type": rt,
            "capacity": info["capacity"],
            "weekday_rate": RATES[rt]["weekday"],
            "weekend_rate": RATES[rt]["weekend"],
        })
    return result


def check_availability(check_in: str | date, check_out: str | date) -> list[dict]:
    """
    Return rooms available for the entire stay.

    Parameters
    ----------
    check_in  : first night (guests arrive this day)
    check_out : departure day (not charged as a night)
    """
    check_in = _parse_date(check_in)
    check_out = _parse_date(check_out)
    if check_out <= check_in:
        raise ValueError("check_out must be after check_in")

    nights = _night_dates(check_in, check_out)
    data = _load()

    available = []
    for room_num, info in ROOMS.items():
        key = str(room_num)
        booked_nights: set[str] = set()
        for booking in data.get(key, []):
            for n in booking["nights"]:
                booked_nights.add(n)

        if any(n.isoformat() in booked_nights for n in nights):
            continue  # at least one night is taken

        rt = info["type"]
        total = sum(_rate_for_night(n, rt) for n in nights)
        available.append({
            "room": room_num,
            "type": rt,
            "capacity": info["capacity"],
            "nights": len(nights),
            "total_cost": round(total, 2),
            "nightly_breakdown": [
                {"date": _night_label(n), "rate": _rate_for_night(n, rt)}
                for n in nights
            ],
        })
    return available


def book_room(
    room: int,
    check_in: str | date,
    check_out: str | date,
    guest_name: str,
) -> dict:
    """
    Book a room for a guest.

    Returns the booking record, or raises ValueError if unavailable.
    """
    check_in = _parse_date(check_in)
    check_out = _parse_date(check_out)
    if check_out <= check_in:
        raise ValueError("check_out must be after check_in")
    if room not in ROOMS:
        raise ValueError(f"Room {room} does not exist (valid: 1-23)")
    if not guest_name.strip():
        raise ValueError("guest_name cannot be empty")

    nights = _night_dates(check_in, check_out)
    data = _load()
    key = str(room)

    # Conflict check
    booked_nights: set[str] = set()
    for booking in data.get(key, []):
        for n in booking["nights"]:
            booked_nights.add(n)

    conflicts = [n.isoformat() for n in nights if n.isoformat() in booked_nights]
    if conflicts:
        raise ValueError(
            f"Room {room} is already booked on: {', '.join(conflicts)}"
        )

    rt = ROOMS[room]["type"]
    breakdown = [
        {"date": _night_label(n), "rate": _rate_for_night(n, rt)}
        for n in nights
    ]
    total = round(sum(b["rate"] for b in breakdown), 2)

    booking_id = f"R{room:02d}-{check_in.isoformat()}-{len(data.get(key, []))+1:03d}"
    record = {
        "booking_id": booking_id,
        "guest": guest_name.strip(),
        "room": room,
        "room_type": rt,
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "nights": [n.isoformat() for n in nights],
        "breakdown": breakdown,
        "total_cost": total,
    }

    data.setdefault(key, []).append(record)
    _save(data)
    return record


def cancel_booking(booking_id: str) -> dict:
    """Cancel a booking by its ID. Returns the cancelled record."""
    data = _load()
    for key, bookings in data.items():
        for i, b in enumerate(bookings):
            if b["booking_id"] == booking_id:
                removed = bookings.pop(i)
                _save(data)
                return removed
    raise ValueError(f"Booking {booking_id!r} not found")


def list_bookings(room: int | None = None) -> list[dict]:
    """List all bookings, optionally filtered by room number."""
    data = _load()
    result = []
    if room is not None:
        result = data.get(str(room), [])
    else:
        for bookings in data.values():
            result.extend(bookings)
    return sorted(result, key=lambda b: (b["room"], b["check_in"]))
