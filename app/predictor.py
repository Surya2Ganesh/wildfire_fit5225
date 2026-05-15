"""
FILE: app/predictor.py
ROLE: Wraps the Ultralytics YOLO library into a single class (YoloPredictor).
      Handles model loading, inference, thread safety, and result formatting.

CALLED FROM: app/main.py
  - predictor = YoloPredictor(MODEL_PATH)   ← called once at server startup
  - predictor.predict(image)                ← called inside run_in_threadpool
  - predictor.build_predict_response(...)   ← called after predict() returns
  - predictor.get_annotated_image(...)      ← called only in /api/annotate

MODEL FILE: fire-models/fire_m.pt
  - Pre-trained YOLO weights for wildfire detection
  - Detects two classes: 0 = fire, 1 = smoke
  - 'm' in fire_m.pt means medium-sized YOLO architecture
"""

from ultralytics import YOLO   # the Ultralytics library that runs YOLO inference
import threading                # used for the Lock to prevent concurrent model access


class YoloPredictor:
    def __init__(self, model_path: str):
        # Load the .pt weights file from disk into memory
        # This is the expensive step (~2-5 seconds) done once at startup
        # After this, self.model holds the complete neural network in RAM
        self.model = YOLO(model_path)

        # threading.Lock() is a mutex — only one thread can hold it at a time
        # WHY NEEDED: run_in_threadpool sends each HTTP request to its own thread.
        # If two requests arrive simultaneously, two threads would call
        # self.model.predict() at the same time. PyTorch's internal state is
        # NOT thread-safe for concurrent calls → race condition → crash or
        # wrong results. The Lock forces inference to run one at a time.
        self.lock = threading.Lock()

    def predict(self, image):
        """
        Run YOLO inference on a single image.
        This method is called from app/main.py via run_in_threadpool().
        It runs in a background thread, NOT on the async event loop.
        """
        # Acquire the lock — if another thread is already inside, this blocks
        # until that thread releases (finishes inference). Only one inference
        # runs at any given moment even if 10 requests arrived simultaneously.
        with self.lock:
            results = self.model.predict(
                source=image,    # the OpenCV NumPy array from utils.decode_base64_image()
                device="cpu",    # force CPU — the OCI VMs have no GPU
                verbose=False    # suppress Ultralytics progress bar spam in logs
            )
        # model.predict() returns a list because it supports batch inference
        # (multiple images at once). We always send one image, so take index [0].
        return results[0]

    def build_predict_response(self, result, request_uuid: str):
        """
        Convert the raw Ultralytics result object into the JSON dict the
        assignment spec requires. Called from app/main.py after predict().

        The spec format:
          uuid, count, detections (list of class names),
          boxes (list of {x, y, width, height, probability}),
          speed_preprocess_ms, speed_inference_ms, speed_postprocess_ms
        """
        detections_output = []   # will hold class name strings e.g. ["fire", "smoke"]
        boxes_output = []        # will hold bounding box dicts

        # self.model.names is a dict like {0: "fire", 1: "smoke"}
        # YOLO stores integer class IDs internally — we convert to readable labels
        names = self.model.names

        if result.boxes is not None:
            # Iterate over every detected object in the image
            for box in result.boxes:
                # box.cls[0] is a tensor holding the integer class ID (0 or 1)
                # .item() converts the tensor scalar to a plain Python int
                cls_id = int(box.cls[0].item())
                class_name = names[cls_id]          # "fire" or "smoke"

                # box.conf[0] is the confidence score (0.0 – 1.0)
                confidence = float(box.conf[0].item())

                # box.xyxy[0] gives [x1, y1, x2, y2] — top-left and bottom-right corners
                # The spec requires top-left corner + width + height format, so we convert
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                width  = x2 - x1    # horizontal span of the bounding box in pixels
                height = y2 - y1    # vertical span of the bounding box in pixels

                detections_output.append(class_name)
                boxes_output.append({
                    "x":           round(x1, 2),
                    "y":           round(y1, 2),
                    "width":       round(width, 2),
                    "height":      round(height, 2),
                    "probability": round(confidence, 4)
                })

        # result.speed is automatically populated by Ultralytics with ms timings
        # for each of the three inference stages: preprocess → inference → postprocess
        # The assignment spec requires all three to be returned in the response
        speed = result.speed if result.speed else {}

        return {
            "uuid":                  request_uuid,
            "count":                 len(detections_output),   # 0 if nothing detected
            "detections":            detections_output,        # [] if nothing detected
            "boxes":                 boxes_output,             # [] if nothing detected
            "speed_preprocess_ms":   round(float(speed.get("preprocess",  0.0)), 2),
            "speed_inference_ms":    round(float(speed.get("inference",   0.0)), 2),
            "speed_postprocess_ms":  round(float(speed.get("postprocess", 0.0)), 2),
        }

    def get_annotated_image(self, result):
        """
        Draw bounding boxes and class labels onto the image and return it
        as a NumPy array. Called from app/main.py in the /api/annotate route.

        result.plot() is a built-in Ultralytics helper — it renders all detected
        boxes onto the original image using OpenCV drawing operations and returns
        the annotated frame as a BGR NumPy array.
        The returned array is then passed to utils.encode_image_to_base64().
        """
        return result.plot()
