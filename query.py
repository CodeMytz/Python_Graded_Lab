"""Running queries against the flight database."""
from validator import is_valid_datetime


def is_valid_query(query) -> bool:
    if not isinstance(query, dict):
        return False

    for key in query:
        value = query[key]

        if key == "flight_id" or key == "origin" or key == "destination":
            if not isinstance(value, str):
                return False
        elif key == "departure_datetime" or key == "arrival_datetime":
            if not isinstance(value, str):
                return False
            if not is_valid_datetime(value):
                return False
        elif key == "price" or key == "min_price":
            if isinstance(value, bool):
                return False
            if not isinstance(value, int) and not isinstance(value, float):
                return False
        elif key == "sort_by":
            if value not in ["flight_id", "origin", "destination", "departure_datetime", "arrival_datetime", "price"]:
                return False
        elif key == "order":
            if value != "asc" and value != "desc":
                return False
        elif key == "limit":
            if isinstance(value, bool) or not isinstance(value, int):
                return False
            if value < 0:
                return False
        else:
            return False

    if "order" in query and "sort_by" not in query:
        return False

    return True

def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = []
    for flight in db:
        match = True

        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            match = False
        if "origin" in query and flight["origin"] != query["origin"]:
            match = False
        if "destination" in query and flight["destination"] != query["destination"]:
            match = False
        if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
            match = False
        if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
            match = False
        if "price" in query and flight["price"] > query["price"]:
            match = False
        if "min_price" in query and flight["price"] < query["min_price"]:
            match = False

        if match:
            matches.append(flight)

    if "sort_by" in query:
        sort_key = query["sort_by"]
        if "order" in query and query["order"] == "desc":
            matches.sort(key=lambda flight: flight[sort_key], reverse=True)
        else:
            matches.sort(key=lambda flight: flight[sort_key])

    if "limit" in query:
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        queries = [queries]

    results = []
    for query in queries:
        results.append(run_query(db, query))

    return results