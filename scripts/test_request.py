"""Small manual test script for sending one image to the local API."""

import base64
import uuid
import requests


def image_to_base64(path: str) -> str:
    """Read a local image file and prepare it for the JSON request body."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# Build the same payload shape that the FastAPI endpoint expects.
payload = {
    "uuid": str(uuid.uuid4()),
    "image": image_to_base64("demo-images/image0.jpeg")
}

# Send the request to the Kubernetes NodePort exposed by the service.
response = requests.post(
    "http://127.0.0.1:30080/api/predict",
    json=payload,
    timeout=120
)

# Print both the HTTP status and parsed JSON so the response is easy to inspect.
print("Status Code:", response.status_code)
print(response.json())
