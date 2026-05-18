from pydantic import BaseModel, Field
from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool

from app.utils import run_yolo_prediction, run_yolo_annotation


# FastAPI application entry point for the CloudEco assignment API.
# The routing layer stays small; YOLO-specific work is handled in app/utils.py.
app = FastAPI(
    title="CloudEco Wildfire Detection API",
    description="FastAPI service for wildfire and smoke detection using YOLO.",
    version="1.0.0"
)


class ImageRequest(BaseModel):
    """
    Request body for both /api/predict and /api/annotate.

    uuid: unique request ID sent by the client.
    image: base64 encoded image string.
    """
    # Pydantic validates that both fields are present before the route runs.
    uuid: str = Field(..., description="Unique request identifier")
    image: str = Field(..., description="Base64 encoded image")


@app.get("/")
def root():
    # Simple landing route to confirm the API container/server is running.
    return {
        "message": "CloudEco Wildfire Detection API is running.",
        "endpoints": ["/api/predict", "/api/annotate", "/health"]
    }


@app.get("/health")
def health():
    # Health endpoint for quick checks and Kubernetes readiness/liveness probes.
    return {
        "status": "healthy"
    }


@app.post("/api/predict")
async def predict(request: ImageRequest):
    """
    Return JSON detections.

    YOLO inference is CPU-heavy and blocking.
    run_in_threadpool prevents it from blocking FastAPI's async event loop.
    """
    # Run the synchronous YOLO function in a worker thread so concurrent
    # HTTP requests are not blocked by one inference call.
    return await run_in_threadpool(
        run_yolo_prediction,
        request.uuid,
        request.image
    )


@app.post("/api/annotate")
async def annotate(request: ImageRequest):
    """
    Return base64 annotated image with YOLO bounding boxes.
    """
    # This endpoint uses the same request schema but returns an annotated
    # image instead of the structured detection list.
    return await run_in_threadpool(
        run_yolo_annotation,
        request.uuid,
        request.image
    )
