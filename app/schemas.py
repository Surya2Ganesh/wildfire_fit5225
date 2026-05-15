"""Pydantic models that define the request and response JSON formats."""

from pydantic import BaseModel, Field
from typing import List


class PredictionRequest(BaseModel):
    """Incoming image payload sent to the API."""
    uuid: str = Field(..., description="Unique request ID")
    image: str = Field(..., description="Base64 encoded image")


class BoxResponse(BaseModel):
    """One detected bounding box in top-left/width/height format."""
    x: float
    y: float
    width: float
    height: float
    probability: float


class PredictResponse(BaseModel):
    """Metadata returned by /api/predict."""
    uuid: str
    count: int
    detections: List[str]
    boxes: List[BoxResponse]
    speed_preprocess_ms: float
    speed_inference_ms: float
    speed_postprocess_ms: float


class AnnotateResponse(BaseModel):
    """Rendered image returned by /api/annotate."""
    uuid: str
    annotated_image: str
