"""
INTERVIEW DEMO SCRIPT — Video Detection
Runs the YOLO model directly on a video file and shows fire/smoke detections
frame by frame in a live pop-up window.

HOW TO RUN:
    python scripts/demo_video.py                           (uses fire1.mp4 by default)
    python scripts/demo_video.py demo-videos/fire4.mp4    (use a different video)

TO CHANGE THE DEFAULT VIDEO: edit line 21 below — change fire1.mp4 to fire3.mp4 or fire4.mp4

CONTROLS (when the video window is open):
    Q or ESC  — quit  (IMPORTANT: click on the video window first, then press Q)
    SPACE     — pause / resume

WHY NOT THROUGH THE API?
    The API accepts one image per HTTP request. Sending 30 frames per second
    over HTTP would be far too slow for smooth video. So this script runs
    YOLO directly on each frame — same model, same weights, just no API call.
"""

import sys
import cv2
from ultralytics import YOLO

# ── CHANGE VIDEO HERE ─────────────────────────────────────────────────────────
# Edit fire1.mp4 to fire3.mp4 or fire4.mp4, or pass a path as a command-line argument:
#   python scripts/demo_video.py demo-videos/fire4.mp4
MODEL_PATH = "fire-models/fire_m.pt"
VIDEO_PATH = "demo-videos/fire3.mp4"

WINDOW_NAME = "Wildfire Detection"

print(f"\n  CloudEco Wildfire Detection — Video Demo")
print(f"  Model : {MODEL_PATH}")
print(f"  Video : {VIDEO_PATH}")
print(f"  CLICK ON THE VIDEO WINDOW then press Q or ESC to quit\n")

# Load the YOLO model once — same fire_m.pt used by the API
model = YOLO(MODEL_PATH)

# Open the video file using OpenCV
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"  ERROR: Could not open video: {VIDEO_PATH}")
    sys.exit(1)

# Create a resizable window so it fits on screen
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 960, 540)

paused = False

while True:
    # Check if the user closed the window by clicking the X button
    if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
        break

    if not paused:
        ret, frame = cap.read()   # read one frame from the video

        if not ret:
            # End of video — loop back to the beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Run YOLO inference on this frame (same model.predict() as in predictor.py)
        results = model.predict(source=frame, device="cpu", verbose=False)

        # results[0].plot() draws bounding boxes and class labels onto the frame
        annotated = results[0].plot()

        # Count how many objects were detected this frame and show it on screen
        detections = results[0].boxes
        count = len(detections) if detections is not None else 0
        cv2.putText(annotated, f"Detections: {count}  |  Q/ESC = quit  SPACE = pause",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Display the annotated frame in a window
        cv2.imshow(WINDOW_NAME, annotated)

    # waitKey(1) waits 1ms for a key press — keeps the window responsive
    # & 0xFF masks to the lower 8 bits (required on some Windows setups)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:   # Q or ESC
        break
    elif key == ord(" "):
        paused = not paused   # toggle pause on/off

# Release the video file and close the display window
cap.release()
cv2.destroyAllWindows()
print("  Video demo ended.")
