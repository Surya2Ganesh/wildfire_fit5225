"""
INTERVIEW DEMO SCRIPT — Image Detection
Sends a fire/smoke image to the running API and shows the results.

HOW TO RUN:
    python scripts/demo.py                          (uses image3.jpeg by default)
    python scripts/demo.py demo-images/image1.jpeg  (use any other image)

TO CHANGE THE DEFAULT IMAGE: edit line 26 below — change image3.jpeg to image0.jpeg, image1.jpeg etc.

WHAT IT DOES:
    1. Calls GET /         → health check (confirms API is running)
    2. Calls POST /api/predict  → prints detections table (class, confidence, bounding box)
    3. Calls POST /api/annotate → saves annotated image and opens it automatically
"""

import base64
import uuid
import requests
import os
import subprocess
import sys

# The API is running locally via Kubernetes NodePort on port 30080
API_BASE = "http://127.0.0.1:30080"

# ── CHANGE IMAGE HERE ─────────────────────────────────────────────────────────
# Edit image3.jpeg to any image in the demo-images/ folder (image0 to image19)
# Or pass a path as a command-line argument: python scripts/demo.py demo-images/image1.jpeg
IMAGE_PATH  = sys.argv[1] if len(sys.argv) > 1 else "demo-images/image3.jpeg"
OUTPUT_PATH = "demo-images/annotated_output.jpg"   # where the annotated image is saved

# ── helpers ───────────────────────────────────────────────────────────────────
def separator(title):
    print("\n" + "=" * 55)
    print(f"  {title}")
    print("=" * 55)

def load_image():
    # Read the image file and encode it to base64 — the API only accepts base64 strings, not raw files
    with open(IMAGE_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def open_image(path):
    # Opens the saved annotated image using the default OS image viewer
    abs_path = os.path.abspath(path)
    if sys.platform == "win32":
        os.startfile(abs_path)
    elif sys.platform == "darwin":
        subprocess.call(["open", abs_path])
    else:
        subprocess.call(["xdg-open", abs_path])

# ── main demo ─────────────────────────────────────────────────────────────────
print("\n  CloudEco Wildfire Detection API — Live Demo")
print("  Model: fire-models/fire_m.pt  |  Classes: fire, smoke")

# Show all available images so you can pick one during the interview
available = sorted([f for f in os.listdir("demo-images") if f.endswith((".jpg", ".jpeg", ".png"))])
print(f"\n  Available images: {', '.join(available)}")
print(f"  Using image    : {IMAGE_PATH}")

# ── STEP 1: Health check ──────────────────────────────────────────────────────
# Hits GET / to confirm the FastAPI server is up and the pod is running
separator("STEP 1 — Health Check  (GET /)")
try:
    r = requests.get(f"{API_BASE}/", timeout=10)
    print(f"  Status : {r.status_code}")
    print(f"  Message: {r.json()['message']}")
except Exception as e:
    print(f"  ERROR: API not reachable — {e}")
    print("  Make sure start_wildfire.ps1 has been run first.")
    sys.exit(1)

# ── STEP 2: /api/predict ──────────────────────────────────────────────────────
# Sends the image as a base64 string in a JSON payload
# The API runs YOLO inference and returns detected classes + bounding boxes
separator("STEP 2 — Object Detection  (POST /api/predict)")
print(f"  Sending image: {IMAGE_PATH}")

image_b64 = load_image()   # image converted to base64 string

# uuid identifies this specific request (required by the API schema)
payload = {"uuid": str(uuid.uuid4()), "image": image_b64}

r = requests.post(f"{API_BASE}/api/predict", json=payload, timeout=120)

if r.status_code != 200:
    print(f"  ERROR {r.status_code}: {r.text}")
    sys.exit(1)

data = r.json()

# Print the response fields from PredictResponse schema
print(f"\n  UUID       : {data['uuid']}")
print(f"  Detections : {data['count']} object(s) found")
print(f"  Classes    : {', '.join(data['detections']) if data['detections'] else 'none'}")
print(f"\n  Preprocess : {data['speed_preprocess_ms']} ms")
print(f"  Inference  : {data['speed_inference_ms']} ms")
print(f"  Postprocess: {data['speed_postprocess_ms']} ms")

# Print a formatted table of each detection with its bounding box coordinates
if data['boxes']:
    print(f"\n  {'#':<4} {'Class':<8} {'Confidence':>10}   {'x':>6} {'y':>6} {'width':>7} {'height':>7}")
    print(f"  {'-'*60}")
    for i, (cls, box) in enumerate(zip(data['detections'], data['boxes']), 1):
        print(f"  {i:<4} {cls:<8} {box['probability']:>10.1%}   "
              f"{box['x']:>6.1f} {box['y']:>6.1f} {box['width']:>7.1f} {box['height']:>7.1f}")

# ── STEP 3: /api/annotate ─────────────────────────────────────────────────────
# Same image sent again — the API draws bounding boxes on the image and returns
# it as a base64 string, which we decode and save as a JPEG file
separator("STEP 3 — Annotated Image  (POST /api/annotate)")
print(f"  Sending same image to /api/annotate ...")

payload2 = {"uuid": str(uuid.uuid4()), "image": image_b64}
r2 = requests.post(f"{API_BASE}/api/annotate", json=payload2, timeout=120)

if r2.status_code != 200:
    print(f"  ERROR {r2.status_code}: {r2.text}")
    sys.exit(1)

data2 = r2.json()
# Decode the base64 annotated image back to bytes and write to a file
img_bytes = base64.b64decode(data2["annotated_image"])

with open(OUTPUT_PATH, "wb") as f:
    f.write(img_bytes)

print(f"  Annotated image saved to: {OUTPUT_PATH}")
print(f"  Opening image now ...")
open_image(OUTPUT_PATH)   # opens the saved image in your default photo viewer

separator("DEMO COMPLETE")
print("  Both endpoints working correctly.")
print(f"  Swagger UI: {API_BASE}/docs")
print()
