"""Reading CSV files into flight records and error messages."""

# Sources used: https://docs.python.org/3/library/os.path.html
import csv
import os
from validator import validate_row, to_record

def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records = []
    errors = []
    seen = set()

    for path in paths:
        file_name = os.path.basename(path)
        line_number = 0

        with open(path, "r") as f:
            for line in f:
                line_number += 1
                line = line.rstrip("\r\n")
                text = line.strip()

                if line_number == 1 or text == "" or text[:1] == "#":
                    continue

                fields = list(csv.reader([line]))[0]
                code = validate_row(fields, airports)

                if code is not None:
                    errors.append(f"{file_name}:{line_number}: {code} | {line}")
                else:
                    record = to_record(fields)
                    key = (record["flight_id"], record["departure_datetime"])
                    if key in seen:
                        errors.append(f"{file_name}:{line_number}: DUPLICATE_FLIGHT | {line}")
                    else:
                        seen.add(key)
                        records.append(record)
    return records, errors