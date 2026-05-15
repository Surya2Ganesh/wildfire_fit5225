import base64
import os
import uuid
from locust import HttpUser, task, between


# This function reads one demo image and converts it to base64.
# We do this once at startup so Locust does not re-read the file every request.
def load_image_base64():
    # Build the image path safely
    image_path = os.path.join(
        os.path.dirname(__file__),   # folder where locustfile.py is
        "..",                        # go back to project root
        "demo-images",
        "image0.jpeg"
    )

    # Convert to absolute path
    image_path = os.path.abspath(image_path)

    # Open image in binary mode and encode it as base64 text
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# Load image once when Locust starts
IMAGE_B64 = load_image_base64()


class WildfireUser(HttpUser):
    # Wait 1 to 2 seconds between requests from the same simulated user
    wait_time = between(1, 2)

    @task(3)
    def predict(self):
        """
        This task sends a request to /api/predict.
        It has weight 3, so it will run more often than /api/annotate.
        """
        payload = {
            "uuid": str(uuid.uuid4()),   # unique ID for each request
            "image": IMAGE_B64           # same demo image each time
        }

        # Send POST request to the prediction endpoint
        self.client.post("/api/predict", json=payload, name="/api/predict")

    @task(1)
    def annotate(self):
        """
        This task sends a request to /api/annotate.
        It has weight 1, so it runs less often than predict.
        """
        payload = {
            "uuid": str(uuid.uuid4()),
            "image": IMAGE_B64
        }

        # Send POST request to the annotation endpoint
        self.client.post("/api/annotate", json=payload, name="/api/annotate")
# Add Locust user tasks here when you want to load-test the wildfire API.
