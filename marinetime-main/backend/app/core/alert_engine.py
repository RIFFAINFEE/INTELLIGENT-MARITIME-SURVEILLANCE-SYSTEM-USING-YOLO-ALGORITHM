import time
import threading
from app.utils.frame_utils import encode_frame


class AlertEngine:
    def __init__(self):

        # key -> last alert timestamp
        self.cooldown = {}

        # thread safety
        self.lock = threading.Lock()

        # seconds before same event can fire again
        self.cooldown_seconds = 5

        print("[ALERT ENGINE] Initialized with cooldown =", self.cooldown_seconds)

    # -------------------------------------------------
    # Check if alert should trigger
    # -------------------------------------------------

    def should_alert(self, camera_id, zone_id, obj_id, event_type):

        key = f"{camera_id}_{zone_id}_{obj_id}_{event_type}"
        now = time.time()

        with self.lock:

            print(
                f"[ALERT CHECK] camera={camera_id} "
                f"zone={zone_id} obj={obj_id} event={event_type}"
            )

            # first alert
            if key not in self.cooldown:

                print("[ALERT ENGINE] First alert -> ALLOWED")

                self.cooldown[key] = now
                return True

            last_time = self.cooldown[key]
            diff = now - last_time

            print(f"[ALERT ENGINE] Time since last alert: {diff:.2f}s")

            # cooldown expired
            if diff > self.cooldown_seconds:

                print("[ALERT ENGINE] Cooldown passed -> ALLOWED")

                self.cooldown[key] = now
                return True

            # duplicate alert
            print("[ALERT ENGINE] Duplicate alert blocked")

            return False

    # -------------------------------------------------
    # Create alert payload
    # -------------------------------------------------

    def create_alert(self, frame, event):

        print("[ALERT ENGINE] Creating alert payload")

        try:
            snapshot = encode_frame(frame)
        except Exception as e:
            print("[ALERT ENGINE] Snapshot encode failed:", e)
            snapshot = None

        payload = {
            "camera_id": event.get("camera_id"),
            "zone_id": event.get("zone_id"),
            "object_id": event["object"]["id"],
            "object_class": event["object"].get("class"),
            "event_type": event.get("type", "zone_event"),
            "timestamp": int(time.time()),
            "snapshot": snapshot,
        }

        print("[ALERT ENGINE] Alert payload created")

        return payload


# -------------------------------------------------
# Singleton instance
# -------------------------------------------------

alert_engine = AlertEngine()