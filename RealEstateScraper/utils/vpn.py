import subprocess
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config.yaml'


def connect(config_path: str | None = None):
    if not config_path:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
            config_path = cfg.get('network', {}).get('vpn_config', '')
    if config_path:
        return subprocess.Popen(['openvpn', '--config', config_path])
    return None


def disconnect(process):
    if process:
        process.terminate()
