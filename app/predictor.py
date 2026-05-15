"""Helpers for running YOLO and shaping its output for the API."""

from ultralytics import YOLO
import threading


class YoloPredictor:
    def __init__(self, model_path: str):
        # Load the model once so repeated API requests stay fast.
        self.model = YOLO(model_path)
        # Ultralytics prediction is wrapped in a lock to avoid overlapping access
        # when multiple requests arrive at the same time.
        self.lock = threading.Lock()

    def predict(self, image):
        """Run inference on a single image and return the first result item."""
        with self.lock:
            results = self.model.predict(
                source=image,
                device="cpu",
                verbose=False
            )
        # The library returns a list because it also supports batches.
        return results[0]

    def build_predict_response(self, result, request_uuid: str):
        """Convert Ultralytics output into the response format expected by clients."""
        detections_output = []
        boxes_output = []

        # Map YOLO class IDs such as 0/1 to readable labels such as fire/smoke.
        names = self.model.names

        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0].item())
                class_name = names[cls_id]
                confidence = float(box.conf[0].item())

                # YOLO stores corners as x1, y1, x2, y2. The API exposes
                # the top-left corner plus width/height because that is easier
                # for many frontend clients to consume.
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                width = x2 - x1
                height = y2 - y1

                detections_output.append(class_name)
                boxes_output.append({
                    "x": round(x1, 2),
                    "y": round(y1, 2),
                    "width": round(width, 2),
                    "height": round(height, 2),
                    "probability": round(confidence, 4)
                })

        # Ultralytics provides stage timings in milliseconds.
        speed = result.speed if result.speed else {}

        return {
            "uuid": request_uuid,
            "count": len(detections_output),
            "detections": detections_output,
            "boxes": boxes_output,
            "speed_preprocess_ms": round(float(speed.get("preprocess", 0.0)), 2),
            "speed_inference_ms": round(float(speed.get("inference", 0.0)), 2),
            "speed_postprocess_ms": round(float(speed.get("postprocess", 0.0)), 2),
        }

    def get_annotated_image(self, result):
        """Render YOLO's boxes and labels back onto the image."""
        return result.plot()
