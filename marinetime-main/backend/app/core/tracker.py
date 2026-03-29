import supervision as sv
import numpy as np


class ByteTrackerWrapper:

    def __init__(self):

        # Improved ByteTrack configuration for stable tracking
        self.tracker = sv.ByteTrack(
            track_activation_threshold=0.25,   # lower → easier track start
            lost_track_buffer=30,              # frames to keep lost objects
            minimum_matching_threshold=0.8,    # stricter matching
            frame_rate=30
        )

    # -----------------------------------------------------

    def update(self, detections):

        if len(detections) == 0:
            return []

        xyxy = []
        conf = []
        cls = []
        names = []

        # Convert detection dict → supervision format
        for d in detections:

            xyxy.append(d["bbox"])
            conf.append(d["score"])
            cls.append(d["class"])
            names.append(d.get("name", "object"))

        det = sv.Detections(
            xyxy=np.array(xyxy),
            confidence=np.array(conf),
            class_id=np.array(cls),
        )

        # Run tracker
        tracks = self.tracker.update_with_detections(det)

        results = []

        for i in range(len(tracks.xyxy)):

            class_id = int(tracks.class_id[i])

            # Safe lookup for class name
            name = "object"
            if class_id < len(names):
                name = names[class_id] if class_id < len(names) else "object"

            results.append(
                {
                    "id": int(tracks.tracker_id[i]),
                    "bbox": tracks.xyxy[i].tolist(),
                    "class": class_id,
                    "name": name,  # 👈 IMPORTANT FOR FRONTEND
                    "score": float(tracks.confidence[i]),
                }
            )

        return results