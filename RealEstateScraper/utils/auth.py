import base64
import os
from pathlib import Path
import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config.yaml'
DATA_PATH = Path(__file__).resolve().parents[1] / 'data'


def _derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))


def save_credentials(site: str, username: str, password: str, master_password: str):
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    salt = os.urandom(16)
    key = _derive_key(master_password, salt)
    token = Fernet(key).encrypt(f"{username}:{password}".encode())
    filepath = DATA_PATH / f"credentials_{site}.bin"
    with open(filepath, 'wb') as f:
        f.write(salt + token)


def load_credentials(site: str, master_password: str | None = None):
    filepath = DATA_PATH / f"credentials_{site}.bin"
    if not filepath.exists() or master_password is None:
        return None
    data = filepath.read_bytes()
    salt, token = data[:16], data[16:]
    key = _derive_key(master_password, salt)
    try:
        decoded = Fernet(key).decrypt(token).decode()
        user, pwd = decoded.split(':', 1)
        return user, pwd
    except Exception:
        return None
