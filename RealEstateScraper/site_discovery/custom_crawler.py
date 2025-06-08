import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config.yaml'

def crawl_from_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    return [(site['name'], site['url']) for site in cfg.get('sites', [])]
