#!/usr/bin/env python3
"""ISBA 2438 Assignment 1: small-store product inventory CLI.

Usage:
    python3 products.py [--file PATH] COMMAND [OPTIONS]

Commands: add, list, get, update, delete, search, lowstock.
Only the Python 3 standard library is used. Each invocation performs
one operation and exits; it never waits for interactive input.

Product records contain exactly four fields:
    id (positive int, assigned automatically, never reused),
    name (trimmed text, at least one non-whitespace character),
    price (string with exactly two decimal places, e.g. "4.50"),
    quantity (non-negative int).

The data file is UTF-8 JSON of the form:
    {"next_id": 1, "products": [...]}
The default file is products.json in the current working directory.
"""

import argparse
import json
import os
import re
import sys
import tempfile

PRICE_RE = re.compile(r"^\d+(?:\.\d{1,2})?$")
INT_RE = re.compile(r"^\d+$")


class StoreError(Exception):
    """Invalid stored data or a file read/write failure (exit code 1)."""


def fail(message, code):
    sys.stderr.write(f"Error: {message}\n")
    raise SystemExit(code)


def positive_int(text):
    if not INT_RE.match(text):
        raise argparse.ArgumentTypeError("ID must be a positive integer")
    value = int(text)
    if value <= 0:
        raise argparse.ArgumentTypeError("ID must be a positive integer")
    return value


def quantity_value(text):
    if not INT_RE.match(text):
        raise argparse.ArgumentTypeError("quantity must be a non-negative integer")
    return int(text)


def price_value(text):
    if not PRICE_RE.match(text):
        raise argparse.ArgumentTypeError(
            "price must be a non-negative decimal with at most two decimal places"
        )
    if "." in text:
        whole, frac = text.split(".", 1)
        frac = frac.ljust(2, "0")
    else:
        whole, frac = text, "00"
    return f"{int(whole)}.{frac}"


def name_value(text):
    value = text.strip()
    if not value:
        raise argparse.ArgumentTypeError("name must contain a non-whitespace character")
    return value


def query_value(text):
    value = text.strip()
    if not value:
        raise argparse.ArgumentTypeError("query must contain a non-whitespace character")
    return value


def validate_store(store):
    if not isinstance(store, dict):
        raise StoreError("stored data is not a JSON object")
    next_id = store.get("next_id")
    products = store.get("products")
    if type(next_id) is not int or next_id <= 0:
        raise StoreError("stored next_id must be a positive integer")
    if not isinstance(products, list):
        raise StoreError("stored products must be an array")
    seen = set()
    max_id = 0
    for product in products:
        if not isinstance(product, dict):
            raise StoreError("stored product is not an object")
        pid = product.get("id")
        name = product.get("name")
        price = product.get("price")
        quantity = product.get("quantity")
        if type(pid) is not int or pid <= 0:
            raise StoreError("stored product id must be a positive integer")
        if pid in seen:
            raise StoreError("stored product ids must be unique")
        seen.add(pid)
        max_id = max(max_id, pid)
        if not isinstance(name, str) or not name.strip() or name != name.strip():
            raise StoreError("stored product name is invalid")
        if not isinstance(price, str) or not re.match(r"^\d+\.\d{2}$", price):
            raise StoreError("stored product price must have exactly two decimal places")
        if type(quantity) is not int or quantity < 0:
            raise StoreError("stored product quantity must be a non-negative integer")
    if next_id <= max_id:
        raise StoreError("stored next_id must be greater than every product id")
    return store


def load_store(path):
    """Return (store, exists). Missing file means an empty store."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except FileNotFoundError:
        return {"next_id": 1, "products": []}, False
    except OSError as exc:
        raise StoreError(f"cannot read data file: {exc}")
    if not raw.strip():
        raise StoreError("data file is empty")
    try:
        text = raw.decode("utf-8")
        store = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StoreError(f"data file is not valid JSON: {exc}")
    return validate_store(store), True


def save_store(path, store):
    """Write the store before reporting success. Do not create parent dirs."""
    data = json.dumps(store, ensure_ascii=False, indent=2) + "\n"
    directory = os.path.dirname(os.path.abspath(path))
    try:
        fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".products-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(data)
            os.replace(tmp_path, path)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except StoreError:
        raise
    except OSError as exc:
        raise StoreError(f"cannot write data file: {exc}")


def print_json(value):
    sys.stdout.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def find_product(store, product_id):
    for product in store["products"]:
        if product["id"] == product_id:
            return product
    return None


def sorted_products(store):
    return sorted(store["products"], key=lambda p: p["id"])


def build_parser():
    parser = argparse.ArgumentParser(
        prog="products.py",
        description="Small-store product inventory CLI. "
        "Run: python3 products.py [--file PATH] COMMAND [OPTIONS]. "
        "Each invocation performs one operation and exits.",
    )
    parser.add_argument(
        "--file",
        dest="file",
        default="products.json",
        metavar="PATH",
        help="JSON data file to use (default: products.json in the current directory). "
        "Must appear before the command.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    p = sub.add_parser("add", help="Create one product.")
    p.add_argument("--name", required=True, type=name_value, help="Product name.")
    p.add_argument("--price", required=True, type=price_value, help="Non-negative price, e.g. 4.50.")
    p.add_argument("--quantity", required=True, type=quantity_value, help="Non-negative integer quantity.")

    sub.add_parser("list", help="Print all products as a JSON array, sorted by id.")

    p = sub.add_parser("get", help="Print one product as a JSON object.")
    p.add_argument("id", type=positive_int, help="Positive integer product id.")

    p = sub.add_parser("update", help="Update one product. At least one field flag is required.")
    p.add_argument("id", type=positive_int, help="Positive integer product id.")
    p.add_argument("--name", type=name_value, help="New product name.")
    p.add_argument("--price", type=price_value, help="New non-negative price, e.g. 4.50.")
    p.add_argument("--quantity", type=quantity_value, help="New non-negative integer quantity.")

    p = sub.add_parser("delete", help="Delete one product. Requires --yes.")
    p.add_argument("id", type=positive_int, help="Positive integer product id.")
    p.add_argument("--yes", required=True, action="store_true", help="Confirm deletion without a prompt.")

    p = sub.add_parser(
        "search",
        help="Custom feature: return products whose name contains the query, ignoring case.",
    )
    p.add_argument("--query", required=True, type=query_value, help="Part of a product name, e.g. Sausage.")

    p = sub.add_parser(
        "lowstock",
        help="Custom feature: return products with quantity at or below a threshold.",
    )
    p.add_argument("--threshold", required=True, type=quantity_value, help="Non-negative integer threshold.")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_usage(sys.stderr)
        sys.stderr.write("Error: a command is required\n")
        return 2

    # update with no field flag is a syntax error (exit 2), checked before
    # reading the data file so a bad call never touches stored data.
    if args.command == "update" and args.name is None and args.price is None and args.quantity is None:
        parser.print_usage(sys.stderr)
        sys.stderr.write("Error: update requires at least one field flag\n")
        return 2

    try:
        store, _exists = load_store(args.file)
    except StoreError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1

    try:
        if args.command == "add":
            product = {
                "id": store["next_id"],
                "name": args.name,
                "price": args.price,
                "quantity": args.quantity,
            }
            store["products"].append(product)
            store["next_id"] += 1
            save_store(args.file, store)
            print_json(product)
            return 0

        if args.command == "list":
            print_json(sorted_products(store))
            return 0

        if args.command == "get":
            product = find_product(store, args.id)
            if product is None:
                sys.stderr.write(f"Error: product {args.id} not found\n")
                return 1
            print_json(product)
            return 0

        if args.command == "update":
            product = find_product(store, args.id)
            if product is None:
                sys.stderr.write(f"Error: product {args.id} not found\n")
                return 1
            if args.name is not None:
                product["name"] = args.name
            if args.price is not None:
                product["price"] = args.price
            if args.quantity is not None:
                product["quantity"] = args.quantity
            save_store(args.file, store)
            print_json(product)
            return 0

        if args.command == "delete":
            product = find_product(store, args.id)
            if product is None:
                sys.stderr.write(f"Error: product {args.id} not found\n")
                return 1
            store["products"] = [p for p in store["products"] if p["id"] != args.id]
            save_store(args.file, store)
            print_json({"deleted_id": args.id})
            return 0

        if args.command == "search":
            needle = args.query.lower()
            matches = [p for p in sorted_products(store) if needle in p["name"].lower()]
            print_json(matches)
            return 0

        if args.command == "lowstock":
            matches = [p for p in sorted_products(store) if p["quantity"] <= args.threshold]
            print_json(matches)
            return 0
    except StoreError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1

    sys.stderr.write("Error: unknown command\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
