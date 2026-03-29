from ultralytics import YOLO
from app.config import settings
import cv2


class YOLOEngine:

    def __init__(self):

        print("[YOLO] Loading model:", settings.YOLO_MODEL)

        self.model = YOLO(settings.YOLO_MODEL)

        # YOLO class names
        self.class_names = self.model.names

        self.conf_threshold = 0.45
        self.iou_threshold = 0.45
        self.inference_size = (640, 360)

        print("[YOLO] Model loaded")
        print("[YOLO] Classes:", self.class_names)

    # -------------------------------------------------

    def detect(self, frame, allowed_classes=None):

        print("\n================ YOLO FRAME =================")

        orig_h, orig_w = frame.shape[:2]
        print(f"[YOLO] Original frame size: {orig_w}x{orig_h}")

        # Resize frame for faster inference
        resized_frame = cv2.resize(frame, self.inference_size)

        print(
            f"[YOLO] Frame resized to "
            f"{self.inference_size[0]}x{self.inference_size[1]}"
        )

        scale_x = orig_w / self.inference_size[0]
        scale_y = orig_h / self.inference_size[1]

        # YOLO inference
        results = self.model(
            resized_frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False
        )[0]

        print("[YOLO] Inference completed")

        all_detections = []
        filtered_detections = []

        if results.boxes is None:
            print("[YOLO] No detections from model")
            return all_detections, filtered_detections

        print(f"[YOLO] Raw detections count: {len(results.boxes)}")

        # -------------------------------------------------
        # Convert allowed class names → YOLO class IDs
        # -------------------------------------------------

        allowed_ids = None

        if allowed_classes and len(allowed_classes) > 0:

            allowed_ids = []

            for cid, cname in self.class_names.items():

                if cname in allowed_classes:
                    allowed_ids.append(cid)

            print("[YOLO] Allowed class names:", allowed_classes)
            print("[YOLO] Allowed class IDs:", allowed_ids)

        # -------------------------------------------------
        # Detection loop
        # -------------------------------------------------

        for box in results.boxes:

            cls = int(box.cls[0])
            score = float(box.conf[0])
            class_name = self.class_names.get(cls, "object")

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # Scale bbox back to original frame size
            x1 *= scale_x
            x2 *= scale_x
            y1 *= scale_y
            y2 *= scale_y

            det = {
                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                "score": score,
                "class": cls,
                "name": class_name
            }

            print(
                f"[YOLO] Detected -> "
                f"id={cls} "
                f"name={class_name} "
                f"score={score:.2f}"
            )

            # Store ALL detections for preview
            all_detections.append(det)

            # -------------------------------------------------
            # Class filtering
            # -------------------------------------------------

            if allowed_ids is not None:

                if cls not in allowed_ids:

                    print(
                        f"[YOLO] Skipped (not allowed) -> "
                        f"class_id={cls} name={class_name}"
                    )

                    continue

                print(
                    f"[YOLO] Accepted -> "
                    f"class_id={cls} name={class_name}"
                )

            filtered_detections.append(det)

        print(
            f"[YOLO] Final detections after filter: "
            f"{len(filtered_detections)}"
        )

        print("=============================================\n")

        return all_detections, filtered_detections


# Global instance
yolo_engine = YOLOEngine()