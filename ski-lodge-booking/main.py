#!/usr/bin/env python3
"""
Ski Lodge Booking System — Interactive CLI
==========================================
Commands
--------
  rooms                              List all 23 rooms with rates
  availability <check-in> <check-out>  Show available rooms
  book <room> <check-in> <check-out> <guest-name>   Book a room
  bookings [room]                    List all (or per-room) bookings
  cancel <booking-id>                Cancel a booking
  help                               Show this message
  quit / exit                        Leave the program

Dates must be in YYYY-MM-DD format.
Weekend rate applies to Friday and Saturday nights.
"""

import sys

import booking as bk


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

RULE = "─" * 72


def _header(title: str) -> None:
    print(f"\n{RULE}")
    print(f"  {title}")
    print(RULE)


def _print_rooms(rooms: list[dict]) -> None:
    _header("All Rooms")
    fmt = "{:<6} {:<10} {:<10} {:>14} {:>14}"
    print(fmt.format("Room", "Type", "Capacity", "Weekday Rate", "Weekend Rate"))
    print("─" * 60)
    for r in rooms:
        print(fmt.format(
            r["room"],
            r["type"],
            r["capacity"],
            f"${r['weekday_rate']:.2f}",
            f"${r['weekend_rate']:.2f}",
        ))


def _print_availability(rooms: list[dict], check_in: str, check_out: str) -> None:
    _header(f"Available Rooms  {check_in} → {check_out}")
    if not rooms:
        print("  No rooms available for this period.")
        return
    fmt = "{:<6} {:<10} {:<10} {:>10} {:>12}"
    print(fmt.format("Room", "Type", "Capacity", "Nights", "Total Cost"))
    print("─" * 52)
    for r in rooms:
        print(fmt.format(
            r["room"],
            r["type"],
            r["capacity"],
            r["nights"],
            f"${r['total_cost']:.2f}",
        ))
        for night in r["nightly_breakdown"]:
            print(f"       {night['date']:<42} ${night['rate']:.2f}")


def _print_booking(b: dict, verb: str = "Booking confirmed") -> None:
    _header(verb)
    print(f"  Booking ID : {b['booking_id']}")
    print(f"  Guest      : {b['guest']}")
    print(f"  Room       : {b['room']} ({b['room_type']})")
    print(f"  Check-in   : {b['check_in']}")
    print(f"  Check-out  : {b['check_out']}")
    print(f"  Nights     : {len(b['nights'])}")
    print()
    for item in b["breakdown"]:
        print(f"    {item['date']:<44} ${item['rate']:.2f}")
    print("─" * 52)
    print(f"  {'TOTAL':.<44} ${b['total_cost']:.2f}")


def _print_bookings(bookings: list[dict]) -> None:
    _header("Bookings")
    if not bookings:
        print("  No bookings found.")
        return
    for b in bookings:
        nights = len(b["nights"])
        print(
            f"  [{b['booking_id']}]  Room {b['room']:>2} ({b['room_type']:<8})  "
            f"{b['check_in']} → {b['check_out']}  "
            f"{nights} night{'s' if nights != 1 else ''}  "
            f"${b['total_cost']:.2f}  —  {b['guest']}"
        )


# ---------------------------------------------------------------------------
# Command dispatch
# ---------------------------------------------------------------------------

def cmd_rooms(_args: list[str]) -> None:
    _print_rooms(bk.list_rooms())


def cmd_availability(args: list[str]) -> None:
    if len(args) < 2:
        print("Usage: availability <check-in YYYY-MM-DD> <check-out YYYY-MM-DD>")
        return
    check_in, check_out = args[0], args[1]
    try:
        rooms = bk.check_availability(check_in, check_out)
        _print_availability(rooms, check_in, check_out)
    except (ValueError, Exception) as e:
        print(f"Error: {e}")


def cmd_book(args: list[str]) -> None:
    if len(args) < 4:
        print("Usage: book <room#> <check-in> <check-out> <guest name…>")
        return
    room_num, check_in, check_out = args[0], args[1], args[2]
    guest = " ".join(args[3:])
    try:
        record = bk.book_room(int(room_num), check_in, check_out, guest)
        _print_booking(record)
    except (ValueError, Exception) as e:
        print(f"Error: {e}")


def cmd_bookings(args: list[str]) -> None:
    room = int(args[0]) if args else None
    try:
        _print_bookings(bk.list_bookings(room))
    except (ValueError, Exception) as e:
        print(f"Error: {e}")


def cmd_cancel(args: list[str]) -> None:
    if not args:
        print("Usage: cancel <booking-id>")
        return
    try:
        removed = bk.cancel_booking(args[0])
        _print_booking(removed, verb="Booking cancelled")
    except (ValueError, Exception) as e:
        print(f"Error: {e}")


def cmd_help(_args: list[str]) -> None:
    print(__doc__)


COMMANDS = {
    "rooms":        cmd_rooms,
    "availability": cmd_availability,
    "book":         cmd_book,
    "bookings":     cmd_bookings,
    "cancel":       cmd_cancel,
    "help":         cmd_help,
}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_interactive() -> None:
    print("Welcome to the Ski Lodge Booking System!")
    print("Type 'help' for a list of commands, or 'quit' to exit.\n")
    while True:
        try:
            line = input("booking> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not line:
            continue
        parts = line.split()
        cmd, *args = parts

        if cmd in ("quit", "exit"):
            print("Goodbye!")
            break
        elif cmd in COMMANDS:
            COMMANDS[cmd](args)
        else:
            print(f"Unknown command: {cmd!r}. Type 'help' for usage.")


def run_from_args(argv: list[str]) -> None:
    """Allow one-shot usage: python main.py availability 2026-01-02 2026-01-05"""
    cmd, *args = argv
    if cmd in COMMANDS:
        COMMANDS[cmd](args)
    else:
        print(f"Unknown command: {cmd!r}")
        cmd_help([])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_from_args(sys.argv[1:])
    else:
        run_interactive()
