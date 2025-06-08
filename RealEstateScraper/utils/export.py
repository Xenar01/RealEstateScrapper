import csv
import json
from pathlib import Path


def export_csv(listings, path):
    keys = listings[0].keys() if listings else []
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(listings)


def export_json(listings, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
