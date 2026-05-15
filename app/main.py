"""FastAPI entry point for wildfire detection inference and annotation."""

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.schemas import PredictionRequest, PredictResponse, AnnotateResponse
from app.utils import decode_base64_image, encode_image_to_base64
from app.predictor import YoloPredictor

# Use the wildfire-specific YOLO model by default for the API service.
MODEL_PATH = "fire-models/fire_m.pt"

app = FastAPI(
    title="CloudEco Wildfire Detection API",
    version="1.0.0"
)

# Load the model once at startup so every request can reuse it.
predictor = YoloPredictor(MODEL_PATH)


@app.get("/")
def root():
    """Simple health endpoint used by users and Kubernetes probes."""
    return {"message": "Wildfire Detection API is running"}


@app.post("/api/predict", response_model=PredictResponse)
async def predict(request: PredictionRequest):
    """Return structured detection metadata for a base64-encoded image."""
    try:
        # Convert the incoming base64 string into an OpenCV image array.
        image = decode_base64_image(request.image)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # YOLO inference is CPU-bound, so run it off the async event loop.
        result = await run_in_threadpool(predictor.predict, image)
        # Translate the raw Ultralytics result into the response schema.
        return predictor.build_predict_response(result, request.uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")


@app.post("/api/annotate", response_model=AnnotateResponse)
async def annotate(request: PredictionRequest):
    """Return the same image with bounding boxes drawn on top of it."""
    try:
        # Reuse the same decoding helper as /api/predict.
        image = decode_base64_image(request.image)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # Run the model first, then turn the result into a rendered image.
        result = await run_in_threadpool(predictor.predict, image)
        annotated = predictor.get_annotated_image(result)
        # Convert the annotated OpenCV image back to base64 for JSON transport.
        encoded = encode_image_to_base64(annotated)

        return {
            "uuid": request.uuid,
            "annotated_image": encoded
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Annotation failed: {e}")
