"""
FILE: app/main.py
ROLE: FastAPI entry point — this is the file uvicorn runs to start the web server.
      It wires together schemas (what JSON looks like), utils (image conversion),
      and predictor (YOLO model) into two HTTP endpoints.

HOW IT IS STARTED:
  - Locally:     uvicorn app.main:app --host 0.0.0.0 --port 8000
  - In Docker:   CMD in Dockerfile runs the same uvicorn command
  - In K8s:      Each pod runs the Docker container, so uvicorn starts automatically

FLOW WHEN A REQUEST ARRIVES:
  Client sends POST /api/predict
    → FastAPI parses JSON into PredictionRequest  (schemas.py)
    → decode_base64_image() converts base64 → OpenCV array  (utils.py)
    → run_in_threadpool runs predictor.predict() in a background thread
    → predictor.build_predict_response() shapes the YOLO result into JSON
    → FastAPI validates output against PredictResponse and returns it
"""

from fastapi import FastAPI, HTTPException
# run_in_threadpool: moves a blocking (CPU-bound) function off the async event loop
# into a thread pool so other requests are not kept waiting
from fastapi.concurrency import run_in_threadpool

# Import the three Pydantic models that define what JSON looks like
from app.schemas import PredictionRequest, PredictResponse, AnnotateResponse
# Import the two image conversion helpers
from app.utils import decode_base64_image, encode_image_to_base64
# Import the class that loads and runs the YOLO model
from app.predictor import YoloPredictor

# Path to the wildfire-specific model weights file (inside fire-models/ folder)
# This is the pre-trained YOLO model that detects Fire and Smoke classes
MODEL_PATH = "fire-models/fire_m.pt"

# Create the FastAPI application object — this is what uvicorn serves
app = FastAPI(
    title="CloudEco Wildfire Detection API",
    version="1.0.0"
    # Swagger UI is auto-generated at http://127.0.0.1:30080/docs
)

# Load the YOLO model ONCE when the server starts up (not on every request)
# Loading takes 2-5 seconds — doing it per-request would make every call very slow
# predictor is a module-level singleton shared by all incoming requests
predictor = YoloPredictor(MODEL_PATH)


# ── Health check ──────────────────────────────────────────────────────────────
# This simple endpoint is used by:
#   1. Kubernetes readinessProbe — is the pod ready to receive traffic?
#   2. Kubernetes livenessProbe  — is the pod still alive?
#   3. Manual testing: curl http://127.0.0.1:30080/
@app.get("/")
def root():
    # Returns immediately with no inference — keeps probes fast and lightweight
    return {"message": "Wildfire Detection API is running"}


# ── /api/predict ──────────────────────────────────────────────────────────────
# Accepts: JSON with uuid (string) + image (base64 string)
# Returns: JSON with detections, bounding boxes, and timing metrics
# Defined in: schemas.py  →  PredictionRequest (input), PredictResponse (output)
@app.post("/api/predict", response_model=PredictResponse)
async def predict(request: PredictionRequest):
    # STEP 1: Decode the base64 image string into an OpenCV NumPy array
    # If the string is corrupt or not a valid image, return HTTP 400 Bad Request
    try:
        image = decode_base64_image(request.image)   # defined in app/utils.py
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # STEP 2: Run YOLO inference
    # CRITICAL: predictor.predict() is CPU-bound and would block the async event
    # loop if called directly. run_in_threadpool() offloads it to a background
    # thread — the event loop stays free to accept new connections while YOLO runs.
    try:
        result = await run_in_threadpool(predictor.predict, image)
        # STEP 3: Convert the raw Ultralytics result object into the JSON format
        # the assignment spec requires (uuid, count, detections, boxes, speed_*)
        return predictor.build_predict_response(result, request.uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")


# ── /api/annotate ─────────────────────────────────────────────────────────────
# Same input as /api/predict but returns the image WITH bounding boxes drawn on it
# The annotated image is base64-encoded back into a string for JSON transport
# Defined in: schemas.py  →  PredictionRequest (input), AnnotateResponse (output)
@app.post("/api/annotate", response_model=AnnotateResponse)
async def annotate(request: PredictionRequest):
    # STEP 1: Same decode as /api/predict — base64 string → OpenCV array
    try:
        image = decode_base64_image(request.image)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # STEP 2: Run YOLO inference (same model, same thread-pool pattern)
        result = await run_in_threadpool(predictor.predict, image)

        # STEP 3: Use Ultralytics' built-in plot() to draw boxes on the image
        # plot() returns a NumPy array with boxes and labels rendered onto it
        annotated = predictor.get_annotated_image(result)  # defined in predictor.py

        # STEP 4: Convert the annotated NumPy array back to a base64 string
        # so it can travel inside the JSON response body
        encoded = encode_image_to_base64(annotated)         # defined in utils.py

        return {
            "uuid": request.uuid,
            "annotated_image": encoded
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Annotation failed: {e}")
