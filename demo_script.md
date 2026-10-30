# A1 recorded demonstration script

Record from a clean directory copy of `products.py` and `README.md`
only, so `products.json` starts missing. Speak in your own words;
do not read this file aloud word for word. Keep the demo short
and show the terminal and the JSON file.

## Part 1 — Required commands (start with no products.json)

```
python3 products.py --help
python3 products.py add --name "Notebook" --price 4.5 --quantity 10
python3 products.py add --name "Pencil" --price 1.25 --quantity 5
python3 products.py list
python3 products.py get 1
python3 products.py update 1 --quantity 12
python3 products.py delete 2 --yes
python3 products.py list
```

Say what to point out: the two adds assign ids 1 and 2, the
final list contains only Notebook with price `"4.50"` and
quantity 12, and the saved `next_id` remains 3. Open
`products.json` on screen and run `list` again to show a later
invocation reads the saved data.

## Part 2 — Persistence, --file, and error behaviour

```
python3 products.py --file demo.json add --name "Notebook" --price 4.50 --quantity 10
python3 products.py --file demo.json list
python3 products.py get 99
python3 products.py add --name "Bad" --price -1 --quantity 5
python3 products.py delete 1
python3 products.py list
```

Say what to point out: `--file` uses a separate file; a missing
id, an invalid price, and a delete without `--yes` each print a
concise error to stderr, exit with the required code, show no
JSON result, and leave the saved data unchanged — run `list`
again after the failures to prove it. Note the exit codes:
missing id = 1, invalid input / delete without `--yes` = 2.

## Part 3 — Custom features (use the deli file)

```
bash seed_deli.sh
python3 products.py --file deli.json search --query Sausage
python3 products.py --file deli.json search --query Tofu
python3 products.py --file deli.json lowstock --threshold 10
python3 products.py --file deli.json lowstock --threshold -1
python3 products.py --file deli.json list
```

Say what to point out, in your own words: `search` finds every
product whose name contains the query ignoring case, so
“Sausage” finds all four sausage products; searching for Tofu
prints `[]` successfully, which is the no-match edge case.
`lowstock --threshold 10` lists the products at or below 10,
which is how staff spot what is about to sell out — sausage
production is irregular, so staff update those quantities by
hand rather than predicting them. A negative threshold is
rejected with exit code 2 and does not change the file.
Finish by showing that the required commands still work on
`deli.json`, for example `get 1`.

## Part 4 — Explain the code and file flow, in your own words

Cover, briefly and without reading code aloud line by line:

- How commands are parsed: one invocation, one operation,
  `--file` before the command, no interactive prompts.
- How each field is validated before anything is saved:
  trimmed non-empty name, price as digits with at most two
  decimals stored as two decimals, non-negative integer
  quantity, positive integer id.
- How ids work: assigned from `next_id`, incremented only on
  a successful add, never changed by update or delete, never
  reused.
- How files work: missing file = empty store, read-only
  commands do not create the file, a successful mutation
  writes the whole store and only then reports success, and
  a failed mutation leaves file bytes and `next_id` unchanged.
- What tool you chose and why: Python 3 standard library
  only, so the tool runs with no third-party packages, and
  plain JSON so a later invocation can read what an earlier
  one saved.
