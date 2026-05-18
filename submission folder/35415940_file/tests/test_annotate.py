import base64
import json
import uuid
from pathlib import Path

import requests


# PROJECT_ROOT points to the main wildfire-detection folder.
# __file__ is this file path:
# wildfire-detection/tests/test_annotate.py
# parents[1] moves two levels up to:
# wildfire-detection/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Input image used for testing the API.
IMAGE_PATH = PROJECT_ROOT / "demo-images" / "image0.jpeg"

# Output image where we will save the annotated result.
OUTPUT_PATH = PROJECT_ROOT / "tests" / "annotated_output.jpeg"

# API endpoint for annotated image prediction.
API_URL = "http://169.224.230.182:30080/api/annotate"


def image_to_base64(path: Path) -> str:
    """
    Convert an image file into a base64 string.

    JSON cannot directly carry binary image data.
    So we convert the image bytes into base64 text before sending it.
    """
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def base64_to_image_file(image_base64: str, output_path: Path) -> None:
    """
    Convert a base64 image string back into an image file.

    The /api/annotate endpoint returns an annotated image as base64.
    This function saves that returned image so we can visually check it.
    """
    image_bytes = base64.b64decode(image_base64)
    with open(output_path, "wb") as output_file:
        output_file.write(image_bytes)


# Create request payload using the same schema required by the assignment:
# uuid + base64 encoded image.
payload = {
    "uuid": str(uuid.uuid4()),
    "image": image_to_base64(IMAGE_PATH)
}

# Send POST request to FastAPI.
response = requests.post(API_URL, json=payload, timeout=60)

print("Image used:", IMAGE_PATH)
print("Status code:", response.status_code)

# Convert response to JSON.
response_json = response.json()

# Print only the uuid and image length.
# We do not print the full base64 image because it is very long.
print(json.dumps({
    "uuid": response_json.get("uuid"),
    "image_base64_length": len(response_json.get("image", ""))
}, indent=2))

# Save the returned annotated image to tests/annotated_output.jpeg
base64_to_image_file(response_json["image"], OUTPUT_PATH)

print("Annotated image saved to:", OUTPUT_PATH)