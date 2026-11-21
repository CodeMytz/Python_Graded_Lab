"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""

# Sources used: https://docs.python.org/3/library/os.path.html https://docs.python.org/3/howto/argparse.html + presentations
import sys
import os
import logging
import argparse
import json

from csv_loader import parse_files
from validator import load_airports
from datetime import datetime
from query import run_queries

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251RDC035"
FIRST_NAME = "Matiss"
LAST_NAME = "Grube"

def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i")
    parser.add_argument("-d")
    parser.add_argument("-j")
    parser.add_argument("-a")
    parser.add_argument("-o")
    parser.add_argument("-q")
    parser.add_argument("-r", default=".")
    return parser

def write_log(log_path: str, errors: list[str]) -> None:
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    try:
        for message in errors:
            logger.warning(message)
    finally:
        logger.removeHandler(handler)
        handler.close()

def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = make_parser()

    try:
        args = parser.parse_args(argv)

        sources = 0
        if args.i is not None:
            sources = sources + 1
        if args.d is not None:
            sources = sources + 1
        if args.j is not None:
            sources = sources + 1

        if sources != 1:
            parser.error("exactly one of -i, -d, -j is required")
        if args.j is None and args.a is None:
            parser.error("-a is required with -i or -d")
        if args.j is not None and args.o is not None:
            parser.error("-o cannot be used with -j")
    except SystemExit as error:
        return error.code

    try:
        if args.j is not None:
            with open(args.j, "r") as f:
                db = json.load(f)
            if not isinstance(db, list):
                print("Error: database file must be a JSON array", file=sys.stderr)
                return 1
        else:
            airports = load_airports(args.a)

            paths = []
            if args.i is not None:
                paths.append(args.i)
            else:
                names = os.listdir(args.d)
                names.sort()
                for name in names:
                    path = os.path.join(args.d, name)
                    if name[-4:] == ".csv" and os.path.isfile(path):
                        paths.append(path)
                if len(paths) == 0:
                    print("Error: no .csv files found", file=sys.stderr)
                    return 1

            db, errors = parse_files(paths, airports)

            if args.o is not None:
                db_path = args.o
            else:
                db_path = "db.json"
            with open(db_path, "w") as f:
                json.dump(db, f)
            write_log(os.path.join(os.path.dirname(db_path), "errors.log"), errors)

        if args.q is not None:
            with open(args.q, "r") as f:
                queries = json.load(f)
            if not isinstance(queries, dict) and not isinstance(queries, list):
                print("Error: query file must be a JSON object or array", file=sys.stderr)
                return 1

            results = run_queries(db, queries)

            now = datetime.now().strftime("%Y%m%d_%H%M")
            file_name = "response_" + STUDENT_ID + "_" + FIRST_NAME + "_" + LAST_NAME + "_" + now + ".json"
            with open(os.path.join(args.r, file_name), "w") as f:
                json.dump(results, f)
    except (OSError, ValueError) as error:
        print("Error: " + str(error), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())