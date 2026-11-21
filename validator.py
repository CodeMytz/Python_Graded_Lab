"""Row validation: airport list loading, single-row checks, record building."""

# Sources used: https://docs.python.org/3.13/library/datetime.html https://docs.python.org/3.13/library/math.html + presentations.,
from datetime import datetime
import math

def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    codes= []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line != "" and line[:1] != "#":
                codes.append(line)
    return {code for code in codes}

# this additional function that I added is a helper function for validate_row to validate date and time. The source used is provided on top of the file.
def is_valid_datetime(text: str) -> bool:
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d %H:%M")
    except ValueError:
        return False
    return parsed.isoformat(" ", "minutes") == text

def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    digits = "0123456789"

    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    flight_id = fields[0].strip()
    origin = fields[1].strip()
    destination = fields[2].strip()
    departure = fields[3].strip()
    arrival = fields[4].strip()
    price = fields[5].strip()

    for field in [flight_id, origin, destination, departure, arrival, price]:
        if field == "":
            return "MISSING_FIELD"

    if len(flight_id) < 2 or len(flight_id) > 8:
        return "INVALID_FLIGHT_ID"
    for char in flight_id:
        if char not in uppercase + lowercase + digits:
            return "INVALID_FLIGHT_ID"

    if len(origin) != 3:
        return "INVALID_ORIGIN"
    for char in origin:
        if char not in uppercase:
            return "INVALID_ORIGIN"
    if origin not in airports:
        return "INVALID_ORIGIN"

    if len(destination) != 3:
        return "INVALID_DESTINATION"
    for char in destination:
        if char not in uppercase:
            return "INVALID_DESTINATION"
    if destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    if not is_valid_datetime(departure):
        return "INVALID_DEPARTURE"

    if not is_valid_datetime(arrival):
        return "INVALID_ARRIVAL"

    if arrival <= departure:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_number = float(price)
    except ValueError:
        return "INVALID_PRICE"
    if price_number != price_number:
        return "INVALID_PRICE"
    if price_number == float("inf") or price_number == float("-inf"):
        return "INVALID_PRICE"

    if price_number <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    record = {}
    record["flight_id"] = fields[0].strip()
    record["origin"] = fields[1].strip()
    record["destination"] = fields[2].strip()
    record["departure_datetime"] = fields[3].strip()
    record["arrival_datetime"] = fields[4].strip()
    record["price"] = float(fields[5].strip())
    return record