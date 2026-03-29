from ultralytics import YOLO


class Detector:

    def __init__(self, model_path):

        self.model = YOLO(model_path)

    def detect(self, frame):

        results = self.model(frame, conf=0.3, verbose=False)[0]

        detections = []

        if results.boxes is None:
            return detections

        for box in results.boxes:

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append(
                {
                    "bbox": [x1, y1, x2, y2],
                    "score": float(box.conf),
                    "class": int(box.cls),
                }
            )

        return detections