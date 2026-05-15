"""Image conversion helpers used by the FastAPI endpoints."""

import base64
import cv2
import numpy as np


def decode_base64_image(base64_str: str) -> np.ndarray:
    """Decode a base64 string from the request body into an OpenCV image."""
    try:
        # Turn the incoming text payload into raw image bytes.
        image_bytes = base64.b64decode(base64_str)
        # Wrap the bytes in a NumPy array so OpenCV can decode them.
        np_arr = np.frombuffer(image_bytes, np.uint8)
        # Read the image in color mode because the model expects 3 channels.
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Image decoding failed")

        return image
    except Exception as e:
        raise ValueError(f"Invalid base64 image: {e}")


def encode_image_to_base64(image: np.ndarray) -> str:
    """Encode an OpenCV image into a base64 string for JSON responses."""
    # Convert the in-memory image matrix into JPEG bytes first.
    success, buffer = cv2.imencode(".jpg", image)
    if not success:
        raise ValueError("Image encoding failed")

    # Base64 makes the binary data safe to embed in JSON.
    return base64.b64encode(buffer.tobytes()).decode("utf-8")
