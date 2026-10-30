# ISBA 2438 — Assignment 1: CLI tool

- Assignment ID: `assignment-1`
- Rubric version: `1.0.0`
- Entry point: `products.py`
- Language: Python 3, standard library only
- Due: November 1, 2026, 11:59 p.m. Pacific

## What this tool does

`products.py` is a small-store product inventory command-line tool.
Each invocation performs one operation and exits; it never waits for
interactive input. Records are saved in a local UTF-8 JSON file with
a `next_id` integer and a `products` array. The default file is
`products.json` in the current working directory.

Product records contain exactly four fields, as required by the
handout:

- `id`: positive integer, assigned automatically from 1, unchanged
  by updates, never reused after deletion.
- `name`: text with at least one non-whitespace character, trimmed.
  Duplicate names are allowed.
- `price`: string with exactly two decimal places, for example
  `"4.50"`. Input may be `0`, `4.5`, or `4.50`; signs, currency
  symbols, exponents, and more than two decimal places are rejected.
- `quantity`: non-negative integer. Zero is allowed; negative or
  fractional quantities are rejected.

## Required commands

The optional `--file PATH` flag must appear before the command:

```
python3 products.py [--file PATH] COMMAND [OPTIONS]
```

| Command | Meaning |
| --- | --- |
| `add --name NAME --price PRICE --quantity QTY` | Create one product, assign the next id, print it as a JSON object. All three flags are required. |
| `list` | Print all products as a JSON array, sorted by id. Prints `[]` when empty. |
| `get ID` | Print the matching product as a JSON object. Error if the id does not exist. |
| `update ID [--name NAME] [--price PRICE] [--quantity QTY]` | At least one field flag is required. Only those fields change; the id and other fields stay the same. Prints the updated product. |
| `delete ID --yes` | `--yes` is required. Deletes the product and prints `{"deleted_id": ID}`. |

`python3 products.py --help` and `python3 products.py <command> --help`
print usage and exit successfully without reading or changing the
data file.

Exit codes: `0` = success (including an empty list or help),
`1` = product id not found, invalid stored data, or file read/write
failure, `2` = invalid command syntax, missing arguments, or invalid
input values. Failures print a concise explanation to standard
error, print no JSON to standard output, produce no traceback, and
do not change the data file or consume an id.

A missing data file is treated as an empty store: `list` prints
`[]`, and `get`, `update`, and `delete` report a missing product.
Read-only commands do not create or rewrite the file. The first
successful `add` creates it. An empty, malformed, or
schema-inconsistent file is reported as an error and left unchanged.
Missing parent directories for a `--file` path are not created.

Example with a separate file:

```
python3 products.py --file demo.json add --name "Notebook" --price 4.50 --quantity 10
```

## Custom features

Two useful features are added on top of the required commands.
Both support `--file`, appear in `--help`, use only the existing
JSON product records, and print a JSON array sorted by id.
They do not change the required commands, output format, file
format, validation, or error behaviour.

### 1. `search` — find products by part of a name

**Who it helps and why:** a shop worker or customer who only
remembers part of a name. In the deli example, searching for
“Sausage” should find every sausage product at once instead of
listing the whole inventory and reading it by eye. This is
especially useful here because sausage production is irregular:
the shop updates availability by hand, so staff need a fast way to
find all sausage records and update them one by one.

**Syntax and inputs:**

```
python3 products.py [--file PATH] search --query TEXT
```

`--query` is required and must contain a non-whitespace
character. Matching ignores case.

**Expected output:** a JSON array of matching products, sorted
by id; `[]` when nothing matches.

**Runnable example:**

```
python3 products.py --file deli.json search --query Sausage
```

If `deli.json` contains Corn Sausage, Garlic Sausage, and Pork
Rib Sausage, the output is those three products as a JSON array.
Searching for a name that is not present, for example
`--query Tofu`, prints `[]` and exits successfully — that is the
edge case: no matching products is a successful empty result,
not an error.

### 2. `lowstock` — report products at or below a threshold

**Who it helps and why:** shop staff checking what is about to
sell out before the day starts, so they can restock, mark an item
sold out, or update tomorrow’s list. It answers “what needs
attention?” without scanning every record.

**Syntax and inputs:**

```
python3 products.py [--file PATH] lowstock --threshold N
```

`--threshold` is required and must be a non-negative integer.

**Expected output:** a JSON array of products whose quantity is
at or below the threshold, sorted by id; `[]` when none qualify.

**Runnable example:**

```
python3 products.py --file deli.json lowstock --threshold 10
```

With the deli demo data below, this returns the products with
quantity 10 or less. A negative or fractional threshold, for
example `--threshold -1` or `--threshold 2.5`, is rejected with
exit code 2 and no change to the data file — that is the edge
case for this feature.

## Deli demo data

The A1 handout allows only the four fields above, so category,
sale type (per piece / per pound), and production schedule are
**not** stored in product records. That is a deliberate limit of
A1, not an omission: later assignments can add those fields.
For the demo, item names come from the Sunnyvale smoked-deli
menu photo, prices are the menu prices per pound or per piece,
and quantities are demo stock numbers in the item’s selling unit
(pounds for per-pound items, pieces for per-piece items).
Sausage production is irregular, so in this demo sausage
availability is updated by hand with `update --quantity ...`,
never predicted from a weekday schedule.

A runnable seed script is in `seed_deli.sh`. It uses a separate
file, `deli.json`, so it does not disturb the required
Notebook/Pencil demonstration in `products.json`:

```
bash seed_deli.sh
python3 products.py --file deli.json list
python3 products.py --file deli.json search --query Sausage
python3 products.py --file deli.json lowstock --threshold 10
```

Seed items (name — price — demo quantity):

- Corn Sausage — 15.00 — 20
- Garlic Sausage — 15.00 — 15
- Pork Rib Sausage — 15.00 — 12
- Signature Large-Cut Pork Sausage — 15.00 — 8
- Smoked Rooster — 32.00 — 6
- Smoked Hen — 16.00 — 10
- Smoked Pig's Trotters — 11.00 — 9
- Smoked Beef Shank — 28.00 — 25
- Sweet & Spicy Duck Neck — 24.00 — 18
- Mala Duck Neck — 20.00 — 5
- Sweet & Sour Duck Wings — 22.00 — 22
- Smoked Chicken Feet — 20.00 — 30

## How the code works, in plain words

Command parsing is done with Python’s standard-library argument
parser, one sub-command per operation, with the global `--file`
flag handled before the command name. Each field has its own
validator: names are trimmed and must not be empty, prices must
match a digits-and-at-most-two-decimals pattern and are then
stored with exactly two decimals, quantities and ids must be
non-negative or positive integers as required. All supplied
values for an update are validated before anything is saved.

For file reading, a missing file is treated as an empty store
with `next_id` 1. An existing file is read as UTF-8, parsed as
JSON, and checked against the required schema: `next_id` must be
a positive integer greater than every existing id, ids must be
unique and positive, names must be non-empty, prices must have
exactly two decimals, and quantities must be non-negative
integers. If that check fails, the command reports an error and
leaves the file untouched.

For file writing, a successful add, update, or delete writes the
whole store to a temporary file in the same directory and then
replaces the data file, so the saved file is only replaced after
a complete write. A failed command never writes, so file bytes
and `next_id` stay unchanged and no id is consumed.

## Submission checklist

- [ ] Python source, including `products.py`, in a public
  GitHub repository.
- [ ] This README, explaining the custom features.
- [ ] A short recorded demonstration (see `demo_script.md`)
  covering the required commands, persistence, error behaviour,
  and the custom features, with a successful use and an edge
  case for each custom feature, and an explanation in your own
  words of the command code and the file read/write flow.
- [ ] In the course portal, submit assignment ID
  `assignment-1`, the repository URL, and the full commit SHA
  for the exact version shown in the recording. Later commits
  do not change that submission; to replace it, submit the new
  SHA through the portal. The portal URL itself is not given
  on the assignment page — use the access details provided by
  the instructor, and report any access problem promptly.
