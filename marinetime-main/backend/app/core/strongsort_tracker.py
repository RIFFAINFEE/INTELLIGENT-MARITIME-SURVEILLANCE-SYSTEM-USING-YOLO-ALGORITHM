from deep_sort_realtime.deepsort_tracker import DeepSort


class StrongSORTTracker:

    def __init__(self, class_names):

        # YOLO class names
        self.class_names = class_names

        # StrongSORT / DeepSort tracker configuration
        self.tracker = DeepSort(
            max_age=120,                 # keep tracks longer (helps maritime scenes)
            n_init=3,                    # frames before track confirmed
            max_cosine_distance=0.4,     # appearance matching threshold
            embedder="mobilenet",        # lightweight ReID model
            half=True,                   # faster inference on GPU
            bgr=True                     # OpenCV uses BGR
        )

    # -------------------------------------------------

    def update(self, detections, frame):

        if not detections:
            return []

        formatted_detections = []

        # Convert YOLO bbox → DeepSort format
        for d in detections:

            x1, y1, x2, y2 = d["bbox"]

            w = x2 - x1
            h = y2 - y1

            formatted_detections.append(
                ([x1, y1, w, h], d["score"], d["class"])
            )

        # Run tracker
        tracks = self.tracker.update_tracks(
            formatted_detections,
            frame=frame
        )

        results = []

        for track in tracks:

            # ignore unconfirmed tracks
            if not track.is_confirmed():
                continue

            track_id = track.track_id

            # DeepSort returns LTWH format
            l, t, w, h = track.to_ltwh()

            r = l + w
            b = t + h

            class_id = track.det_class

            name = self.class_names.get(class_id, "object")

            results.append(
                {
                    "id": int(track_id),
                    "bbox": [float(l), float(t), float(r), float(b)],
                    "class": int(class_id),
                    "name": name,
                    "score": float(track.det_conf) if track.det_conf else 0.0
                }
            )

        return results