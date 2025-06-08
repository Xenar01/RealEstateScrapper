import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RealEstateScraper.utils import dedup, export


def test_deduplicate():
    items = [
        {'title': 'A', 'price': '1', 'location': 'x'},
        {'title': 'A', 'price': '1', 'location': 'x'},
        {'title': 'B', 'price': '2', 'location': 'y'},
    ]
    result = dedup.deduplicate(items)
    assert len(result) == 2


def test_export(tmp_path):
    data = [{'a': 1}, {'a': 2}]
    csv_path = tmp_path / 'data.csv'
    json_path = tmp_path / 'data.json'
    export.export_csv(data, csv_path)
    export.export_json(data, json_path)
    assert csv_path.exists() and json_path.exists()
    assert json.loads(json_path.read_text()) == data
