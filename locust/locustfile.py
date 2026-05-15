"""
FILE: locust/locustfile.py
ROLE: Load-testing script. Simulates multiple concurrent users sending real
      image inference requests to the running API.

HOW TO RUN:
  locust -f locust/locustfile.py --host http://127.0.0.1:30080
  Then open http://localhost:8089 in a browser to control the test.

WHAT IT DOES:
  - Reads demo-images/image0.jpeg from disk and base64-encodes it ONCE at startup
  - Creates N virtual users (WildfireUser instances), each running tasks in a loop
  - Each user alternates between /api/predict (75% of the time) and /api/annotate (25%)
  - Locust records response times and failure rates for the benchmark report

WHY ENCODE ONCE AT MODULE LEVEL:
  Base64 encoding is CPU work. If 100 users each encoded on every request,
  Locust itself would become the bottleneck and measured latency would include
  client encoding time, not just server inference time. Encoding once and
  sharing IMAGE_B64 across all users keeps the measurement accurate.
"""

import base64   # to encode the image file into base64 text
import os       # to build a cross-platform file path to the demo image
import uuid     # to generate a unique ID for each request
from locust import HttpUser, task, between
# HttpUser  — base class for a simulated user that makes HTTP requests
# task      — decorator that marks a method as a load-test task
# between   — generates a random wait time between two values


def load_image_base64():
    """
    Read demo-images/image0.jpeg from disk and return it as a base64 string.
    Called once at module load time (when Locust starts), not per-request.

    os.path.dirname(__file__) = the folder containing locustfile.py (locust/)
    ".."                      = go up one level to the project root
    "demo-images/image0.jpeg" = the test image used for all load-test requests
    """
    image_path = os.path.join(
        os.path.dirname(__file__),   # locust/
        "..",                        # project root
        "demo-images",
        "image0.jpeg"
    )
    image_path = os.path.abspath(image_path)   # resolve to full absolute path

    # Open binary ("rb") — images are binary files, not text
    with open(image_path, "rb") as f:
        # base64.b64encode() → bytes, .decode("utf-8") → str
        return base64.b64encode(f.read()).decode("utf-8")


# Load and encode the image ONCE when Locust imports this file
# All WildfireUser instances will share this same pre-encoded string
IMAGE_B64 = load_image_base64()


class WildfireUser(HttpUser):
    """
    Simulates one concurrent user hitting the Wildfire Detection API.
    Locust creates N instances of this class (N = number of users you set in the UI).
    Each instance runs tasks independently in its own "green thread" (coroutine).
    """

    # After finishing each task, wait a random time between 1 and 2 seconds
    # before starting the next one. This simulates realistic human think time
    # and prevents perfectly synchronised request bursts.
    wait_time = between(1, 2)

    @task(3)
    def predict(self):
        """
        Sends a POST request to /api/predict.
        Weight = 3 → this task is chosen 3 out of every 4 task selections.
        (3 predict requests for every 1 annotate request)

        /api/predict is the primary endpoint — lighter than annotate because
        it does not need to render bounding boxes onto the image.
        """
        payload = {
            # Generate a fresh UUID for every request so the server can correlate
            # each async response to its original request (as per assignment spec)
            "uuid":  str(uuid.uuid4()),
            # Reuse the pre-encoded image — same image every time, different UUID
            "image": IMAGE_B64
        }

        # self.client is Locust's built-in HTTP session (wraps the requests library)
        # json=payload → sets Content-Type: application/json and serialises the dict
        # name="/api/predict" → groups all predict requests together in Locust's stats UI
        self.client.post("/api/predict", json=payload, name="/api/predict")

    @task(1)
    def annotate(self):
        """
        Sends a POST request to /api/annotate.
        Weight = 1 → this task is chosen 1 out of every 4 task selections.

        /api/annotate is heavier than /api/predict because after inference
        it also runs result.plot() to draw boxes and then re-encodes the image.
        Running it less frequently reflects realistic usage patterns.
        """
        payload = {
            "uuid":  str(uuid.uuid4()),
            "image": IMAGE_B64
        }

        self.client.post("/api/annotate", json=payload, name="/api/annotate")
