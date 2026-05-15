"""
FILE: app/utils.py
ROLE: Two image conversion helper functions used by app/main.py.
      Bridges between the JSON world (Base64 strings) and the OpenCV world
      (NumPy arrays) that YOLO requires.

CALLED FROM: app/main.py
  - decode_base64_image()  → called at the start of both predict() and annotate()
                             to turn the incoming base64 string into an image array
  - encode_image_to_base64() → called in annotate() to turn the annotated NumPy
                               array back into a base64 string for the JSON response

WHY BASE64?
  HTTP JSON bodies are text-only. Raw image bytes (JPEG = binary) cannot be safely
  embedded in a JSON string field. Base64 encoding converts every 3 bytes of binary
  into 4 printable ASCII characters, making it safe to put inside JSON.
  The tradeoff: Base64 is ~33% larger than the original binary.
"""

import base64   # Python standard library — encodes/decodes base64
import cv2      # OpenCV — reads and writes image files, used by YOLO
import numpy as np  # NumPy — the array format OpenCV and YOLO both use


def decode_base64_image(base64_str: str) -> np.ndarray:
    """
    Convert a Base64-encoded image string (from the JSON request body)
    into an OpenCV BGR NumPy array that can be passed directly to YOLO.

    Pipeline:
      base64 string  →  raw bytes  →  NumPy uint8 array  →  OpenCV image array

    CALLED FROM: app/main.py → predict() and annotate()
    RETURNS: np.ndarray with shape (height, width, 3) and dtype uint8
    RAISES: ValueError if the string is not valid base64 or not a valid image
    """
    try:
        # Step 1: base64.b64decode() converts the ASCII text back into raw binary bytes
        # These bytes are the actual JPEG/PNG file content (compressed image format)
        image_bytes = base64.b64decode(base64_str)

        # Step 2: np.frombuffer() wraps the bytes in a 1D NumPy uint8 array
        # This is required because cv2.imdecode expects a NumPy array, not raw bytes
        # np.frombuffer does NOT copy data — it is a zero-copy view of the same memory
        np_arr = np.frombuffer(image_bytes, np.uint8)

        # Step 3: cv2.imdecode() decompresses the JPEG/PNG bytes into a pixel array
        # IMREAD_COLOR ensures we always get 3 channels (BGR) — YOLO requires 3 channels
        # If IMREAD_GRAYSCALE were used instead, the image would be (H, W) not (H, W, 3)
        # and YOLO would throw a shape mismatch error
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # cv2.imdecode returns None if the bytes are corrupted or not a real image
        # We raise a clear error rather than passing None to YOLO (which would crash)
        if image is None:
            raise ValueError("Image decoding failed — bytes may be corrupt or not an image")

        return image   # shape: (H, W, 3), dtype: uint8, colour order: BGR

    except Exception as e:
        # Wrap any exception in a ValueError so main.py can catch it
        # and return HTTP 400 (client's fault) instead of HTTP 500 (server's fault)
        raise ValueError(f"Invalid base64 image: {e}")


def encode_image_to_base64(image: np.ndarray) -> str:
    """
    Convert an OpenCV BGR NumPy array (the annotated image from result.plot())
    back into a Base64-encoded string for embedding in the JSON response.

    Pipeline:
      OpenCV NumPy array  →  JPEG bytes  →  Base64 string

    CALLED FROM: app/main.py → annotate()
    RETURNS: str — a Base64 ASCII string the client can decode to get the image
    RAISES: ValueError if the image array cannot be JPEG-encoded
    """
    # Step 1: cv2.imencode() compresses the NumPy pixel array into JPEG format
    # Returns (success_bool, buffer_array)
    # The ".jpg" extension tells OpenCV to use JPEG compression
    success, buffer = cv2.imencode(".jpg", image)

    if not success:
        raise ValueError("Image encoding failed — could not compress array to JPEG")

    # Step 2: buffer.tobytes() converts the NumPy buffer into standard Python bytes
    # Step 3: base64.b64encode() converts binary bytes into Base64 ASCII bytes
    # Step 4: .decode("utf-8") converts the ASCII bytes into a plain Python string
    # This string is what gets inserted into the "annotated_image" field of the JSON response
    return base64.b64encode(buffer.tobytes()).decode("utf-8")
