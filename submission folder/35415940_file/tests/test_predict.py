import base64
import json
import uuid
from pathlib import Path

import requests


# Because this file is inside tests/, we use project root path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

IMAGE_PATH = PROJECT_ROOT / "demo-images" / "image0.jpeg"
API_URL = "http://169.224.230.182:30080/api/predict"


def image_to_base64(path: Path) -> str:
    """
    Read an image file and convert it into a base64 string.
    """
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


payload = {
    "uuid": str(uuid.uuid4()),
    "image": image_to_base64(IMAGE_PATH)
}

response = requests.post(API_URL, json=payload, timeout=60)

print("Image used:", IMAGE_PATH)
print("Status code:", response.status_code)

try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)