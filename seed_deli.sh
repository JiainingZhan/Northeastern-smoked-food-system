#!/bin/bash
# Seed deli demo data into a SEPARATE file (deli.json), so the required
# Notebook/Pencil demonstration in products.json is not disturbed.
# Quantities are demo stock numbers in the item's selling unit
# (pounds for per-pound items, pieces for per-piece items).
set -e
cd "$(dirname "$0")"
rm -f deli.json
python3 products.py --file deli.json add --name "Corn Sausage" --price 15.00 --quantity 20
python3 products.py --file deli.json add --name "Garlic Sausage" --price 15.00 --quantity 15
python3 products.py --file deli.json add --name "Pork Rib Sausage" --price 15.00 --quantity 12
python3 products.py --file deli.json add --name "Signature Large-Cut Pork Sausage" --price 15.00 --quantity 8
python3 products.py --file deli.json add --name "Smoked Rooster" --price 32.00 --quantity 6
python3 products.py --file deli.json add --name "Smoked Hen" --price 16.00 --quantity 10
python3 products.py --file deli.json add --name "Smoked Pig's Trotters" --price 11.00 --quantity 9
python3 products.py --file deli.json add --name "Smoked Beef Shank" --price 28.00 --quantity 25
python3 products.py --file deli.json add --name "Sweet & Spicy Duck Neck" --price 24.00 --quantity 18
python3 products.py --file deli.json add --name "Mala Duck Neck" --price 20.00 --quantity 5
python3 products.py --file deli.json add --name "Sweet & Sour Duck Wings" --price 22.00 --quantity 22
python3 products.py --file deli.json add --name "Smoked Chicken Feet" --price 20.00 --quantity 30
echo "Seeded deli.json with 12 products."
