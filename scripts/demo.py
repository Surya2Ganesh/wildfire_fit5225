"""
INTERVIEW DEMO SCRIPT
Run this to show the interviewer both API endpoints working live.

HOW TO RUN:
    python scripts/demo.py

WHAT IT DOES:
    1. Sends a fire image to /api/predict  → prints detections + bounding boxes
    2. Sends the same image to /api/annotate → saves + opens the annotated image
"""

import base64
import uuid
import requests
import os
import subprocess
import sys

API_BASE = "http://127.0.0.1:30080"

# Use image from command line if provided, otherwise default to image0.jpeg
# Usage:  python scripts/demo.py
#         python scripts/demo.py demo-images/image1.jpeg
#         python scripts/demo.py C:\Users\surya\Desktop\anyimage.jpg
IMAGE_PATH  = sys.argv[1] if len(sys.argv) > 1 else "demo-images/image0.jpeg"
OUTPUT_PATH = "demo-images/annotated_output.jpg"

# ── helpers ───────────────────────────────────────────────────────────────────
def separator(title):
    print("\n" + "=" * 55)
    print(f"  {title}")
    print("=" * 55)

def load_image():
    with open(IMAGE_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def open_image(path):
    """Open an image file with the default OS viewer."""
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

# Show all available demo images so you can pick one during the interview
available = sorted([f for f in os.listdir("demo-images") if f.endswith((".jpg", ".jpeg", ".png"))])
print(f"\n  Available images: {', '.join(available)}")
print(f"  Using image    : {IMAGE_PATH}")

# Step 0 — health check
separator("STEP 1 — Health Check  (GET /)")
try:
    r = requests.get(f"{API_BASE}/", timeout=10)
    print(f"  Status : {r.status_code}")
    print(f"  Message: {r.json()['message']}")
except Exception as e:
    print(f"  ERROR: API not reachable — {e}")
    print("  Make sure start_wildfire.ps1 has been run first.")
    sys.exit(1)

# Step 1 — /api/predict
separator("STEP 2 — Object Detection  (POST /api/predict)")
print(f"  Sending image: {IMAGE_PATH}")

image_b64 = load_image()
payload = {"uuid": str(uuid.uuid4()), "image": image_b64}

r = requests.post(f"{API_BASE}/api/predict", json=payload, timeout=120)

if r.status_code != 200:
    print(f"  ERROR {r.status_code}: {r.text}")
    sys.exit(1)

data = r.json()

print(f"\n  UUID       : {data['uuid']}")
print(f"  Detections : {data['count']} object(s) found")
print(f"  Classes    : {', '.join(data['detections']) if data['detections'] else 'none'}")
print(f"\n  Preprocess : {data['speed_preprocess_ms']} ms")
print(f"  Inference  : {data['speed_inference_ms']} ms")
print(f"  Postprocess: {data['speed_postprocess_ms']} ms")

if data['boxes']:
    print(f"\n  {'#':<4} {'Class':<8} {'Confidence':>10}   {'x':>6} {'y':>6} {'width':>7} {'height':>7}")
    print(f"  {'-'*60}")
    for i, (cls, box) in enumerate(zip(data['detections'], data['boxes']), 1):
        print(f"  {i:<4} {cls:<8} {box['probability']:>10.1%}   "
              f"{box['x']:>6.1f} {box['y']:>6.1f} {box['width']:>7.1f} {box['height']:>7.1f}")

# Step 2 — /api/annotate
separator("STEP 3 — Annotated Image  (POST /api/annotate)")
print(f"  Sending same image to /api/annotate ...")

payload2 = {"uuid": str(uuid.uuid4()), "image": image_b64}
r2 = requests.post(f"{API_BASE}/api/annotate", json=payload2, timeout=120)

if r2.status_code != 200:
    print(f"  ERROR {r2.status_code}: {r2.text}")
    sys.exit(1)

data2 = r2.json()
img_bytes = base64.b64decode(data2["annotated_image"])

with open(OUTPUT_PATH, "wb") as f:
    f.write(img_bytes)

print(f"  Annotated image saved to: {OUTPUT_PATH}")
print(f"  Opening image now ...")
open_image(OUTPUT_PATH)

separator("DEMO COMPLETE")
print("  Both endpoints working correctly.")
print(f"  Swagger UI: {API_BASE}/docs")
print()
