import base64
from pathlib import Path


def webp_data_uri(path: Path) -> str:
    data = path.read_bytes()
    return "data:image/webp;base64," + base64.b64encode(data).decode("ascii")