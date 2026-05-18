import base64
import uuid
from pathlib import Path

from locust import HttpUser, between, task


# This file location:
# wildfire-detection/locust/locustfile.py
#
# parents[1] points to:
# wildfire-detection/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Test image used by Locust.
IMAGE_PATH = PROJECT_ROOT / "demo-images" / "image0.jpeg"


def image_to_base64(path: Path) -> str:
    """
    Convert the demo image into a base64 string.

    The assignment API requires image data inside JSON,
    so Locust must send the image as base64 text.
    """
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Load the image once when Locust starts.
# This avoids reading the file again for every request.
IMAGE_BASE64 = image_to_base64(IMAGE_PATH)


class WildfireApiUser(HttpUser):
    """
    Simulated user for load testing the deployed FastAPI YOLO service.

    Locust will create many virtual users from this class.
    Each user repeatedly sends requests to /api/predict and /api/annotate.
    """

    # Wait time between requests from each simulated user.
    wait_time = between(1, 3)

    @task(3)
    def predict(self):
        """
        Send request to /api/predict.

        Weight 3 means this task runs more often than annotate.
        This is useful because JSON prediction is the main benchmark endpoint.
        """
        payload = {
            "uuid": str(uuid.uuid4()),
            "image": IMAGE_BASE64
        }

        with self.client.post(
            "/api/predict",
            json=payload,
            name="/api/predict",
            catch_response=True,
            timeout=60
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
                return

            data = response.json()

            # Validate required assignment response fields.
            required_fields = [
                "uuid",
                "count",
                "detections",
                "boxes",
                "speed_preprocess_ms",
                "speed_inference_ms",
                "speed_postprocess_ms"
            ]

            for field in required_fields:
                if field not in data:
                    response.failure(f"Missing field: {field}")
                    return

            response.success()

    @task(1)
    def annotate(self):
        """
        Send request to /api/annotate.

        Weight 1 means this runs less often because annotated image responses
        are larger and usually slower than JSON prediction.
        """
        payload = {
            "uuid": str(uuid.uuid4()),
            "image": IMAGE_BASE64
        }

        with self.client.post(
            "/api/annotate",
            json=payload,
            name="/api/annotate",
            catch_response=True,
            timeout=60
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
                return

            data = response.json()

            # Validate annotated image response.
            if "uuid" not in data:
                response.failure("Missing field: uuid")
                return

            if "image" not in data:
                response.failure("Missing field: image")
                return

            response.success()