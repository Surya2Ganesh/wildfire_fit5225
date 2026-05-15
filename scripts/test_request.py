"""
FILE: scripts/test_request.py
ROLE: A simple one-shot manual test script. Sends a single real image to the
      /api/predict endpoint and prints the full JSON response.
      Used to verify the API is working correctly during the interview demo.

HOW TO RUN:
  python scripts/test_request.py
  (Run from the project root — the image path is relative to the project root)

WHAT IT DOES:
  1. Reads demo-images/image0.jpeg from disk
  2. Base64-encodes it
  3. POSTs JSON to http://127.0.0.1:30080/api/predict (the Kubernetes NodePort)
  4. Prints the HTTP status code and the full JSON response body

WHY PORT 30080?
  30080 is the Kubernetes NodePort — traffic here goes through the K8s Service
  which routes to the pod on port 8000. This is the real production path,
  not a shortcut directly to the container.
"""

import base64    # to encode the image into base64 text for the JSON body
import uuid      # to generate a unique request ID as required by the spec
import requests  # HTTP client library (installed via requirements_a1.txt)


def image_to_base64(path: str) -> str:
    """
    Read an image file from disk and return it as a base64-encoded ASCII string.
    The string is safe to embed inside a JSON field ("image": "...").

    path: relative path from the project root (e.g. "demo-images/image0.jpeg")
    """
    with open(path, "rb") as f:          # open in binary mode — image is not text
        return base64.b64encode(f.read()).decode("utf-8")
        # base64.b64encode() → bytes object
        # .decode("utf-8")   → Python string (JSON-safe ASCII)


# Build the JSON payload matching the PredictionRequest schema in app/schemas.py
# uuid: a fresh UUID4 string — uniquely identifies this specific request
# image: the base64-encoded JPEG file content
payload = {
    "uuid":  str(uuid.uuid4()),
    "image": image_to_base64("demo-images/image0.jpeg")
}

# Send the POST request to the Kubernetes NodePort
# timeout=120 allows up to 2 minutes — YOLO on CPU can be slow under load
# The API is at 127.0.0.1 because Docker Desktop's K8s exposes NodePorts on localhost
response = requests.post(
    "http://127.0.0.1:30080/api/predict",
    json=payload,       # sets Content-Type: application/json and serialises payload
    timeout=120
)

# Print results — Status 200 = success, anything else = investigate
print("Status Code:", response.status_code)
# response.json() parses the response body as JSON into a Python dict
# This dict should match the PredictResponse schema in app/schemas.py:
# { uuid, count, detections, boxes, speed_preprocess_ms, speed_inference_ms, speed_postprocess_ms }
print(response.json())
