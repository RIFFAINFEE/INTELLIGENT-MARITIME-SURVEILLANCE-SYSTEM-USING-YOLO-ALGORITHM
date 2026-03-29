import threading
import time
import cv2
import asyncio
import logging

from app.core.async_stream import AsyncVideoStream
from app.core.yolo_engine import yolo_engine
from app.core.strongsort_tracker import StrongSORTTracker
from app.core.zone_crossing import ZoneCrossingEngine
from app.core.alert_storage import alert_storage
from app.core.alert_engine import alert_engine
from app.core.zone_store import zone_store
from app.websocket_manager import ws_manager

logger = logging.getLogger("stream_worker")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


class StreamWorker:

    def __init__(self):

        self.cameras = {}
        self.latest_frames = {}
        self.latest_detections = {}

        self.running = False
        self.loop_delay = 0.01

        # NEW: cross-frame deduplication
        self.recent_events = {}
        self.event_cooldown = 2  # seconds

        logger.info("[Worker] Initialized")

    @property
    def stream_count(self):
        return len(self.cameras)

    def start(self):

        if self.running:
            return

        self.running = True

        thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        thread.start()

        logger.info("[Worker] Thread started")

    def add_camera(self, camera_id, url, allowed_classes=None):

        if camera_id in self.cameras:
            logger.warning(f"[Worker] Camera already exists: {camera_id}")
            return

        stream = AsyncVideoStream(url).start()
        tracker = StrongSORTTracker(yolo_engine.class_names)
        zone_crossing = ZoneCrossingEngine()

        self.cameras[camera_id] = {
            "stream": stream,
            "tracker": tracker,
            "crossing": zone_crossing,
            "allowed_classes": allowed_classes or []
        }

        self.latest_frames[camera_id] = None
        self.latest_detections[camera_id] = []

        logger.info(f"[Worker] Camera added: {camera_id}")

    def remove_camera(self, camera_id):

        if camera_id not in self.cameras:
            return

        cam = self.cameras[camera_id]

        try:
            cam["stream"].stop()
        except Exception as e:
            logger.warning(f"[Worker] Stream stop error: {e}")

        del self.cameras[camera_id]

        self.latest_frames.pop(camera_id, None)
        self.latest_detections.pop(camera_id, None)

        logger.info(f"[Worker] Camera removed: {camera_id}")

    def send_alert_ws(self, payload):

        try:

            if ws_manager.loop is None:
                logger.warning("[WebSocket] Event loop not ready")
                return

            asyncio.run_coroutine_threadsafe(
                ws_manager.broadcast(payload),
                ws_manager.loop
            )

            logger.info(f"[WebSocket] Alert sent: {payload}")

        except Exception as e:
            logger.error(f"[WebSocket Error] {e}")

    def process_camera(self, cam_id, cam):

        try:

            frame = cam["stream"].read()

            if frame is None:
                return

            frame_h, frame_w = frame.shape[:2]

            zones = zone_store.by_camera(cam_id)

            scaled_zones = []

            for z in zones:

                scaled_points = []

                for px, py in z["points"]:
                    x = px * frame_w
                    y = py * frame_h
                    scaled_points.append([x, y])

                scaled_zones.append({
                    "id": z["id"],
                    "points": scaled_points
                })

            cam["crossing"].update_zones(scaled_zones)

            all_detections, detections = yolo_engine.detect(
                frame,
                cam["allowed_classes"]
            )

            self.latest_detections[cam_id] = all_detections

            logger.info(f"[YOLO] Camera={cam_id} detections={len(detections)}")

            tracked = cam["tracker"].update(detections, frame) if detections else []

            logger.info(f"[TRACKER] Camera={cam_id} tracked={len(tracked)}")

            for obj in tracked:

                x1, y1, x2, y2 = map(int, obj["bbox"])

                label = f"{obj.get('name','object')} #{obj['id']}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,255,0),
                    2
                )

            crossing_events = cam["crossing"].check(tracked)

            sent_events = set()

            for e in crossing_events:

                obj = e["object"]
                zone_id = e["zone_id"]
                event_type = e["type"]
                obj_id = obj["id"]

                event_key = f"{cam_id}_{zone_id}_{obj_id}_{event_type}"

                # block duplicates in same frame
                if event_key in sent_events:
                    continue

                sent_events.add(event_key)

                # block duplicates across frames
                now = time.time()
                last = self.recent_events.get(event_key)

                if last and (now - last) < self.event_cooldown:
                    logger.info(f"[DEDUP] Skipping duplicate {event_key}")
                    continue

                self.recent_events[event_key] = now

                class_name = obj.get("name", "object")

                logger.info(
                    f"[CROSSING] Camera={cam_id} "
                    f"{class_name} #{obj_id} {event_type} zone={zone_id}"
                )

                if alert_engine.should_alert(cam_id, zone_id, obj_id, event_type):

                    # Calculate Lat/Long for Chennai Coastal Mapping
                    # Bounding Box: [x1, y1, x2, y2]
                    x1, y1, x2, y2 = obj["bbox"]
                    cx_percent = ((x1 + x2) / 2) / frame_w
                    cy_percent = ((y1 + y2) / 2) / frame_h

                    # Mapping to Chennai coastal range:
                    # Lat: 13.00 (South) to 13.20 (North) -> cy=1.0 is South, cy=0.0 is North
                    # Lon: 80.25 (West) to 80.35 (East) -> cx=0.0 is West, cx=1.0 is East
                    obj_lat = 13.20 - (cy_percent * 0.20)
                    obj_lon = 80.25 + (cx_percent * 0.10)

                    saved_alert = alert_storage.save(
                        frame, cam_id, zone_id, obj_id,
                        object_name=class_name,
                        lat=round(obj_lat, 6),
                        lon=round(obj_lon, 6)
                    )

                    self.send_alert_ws({
                        "type": "zone_crossing",
                        "camera_id": cam_id,
                        "zone_id": zone_id,
                        "object": class_name,
                        "object_id": obj_id,
                        "event": event_type,
                        "timestamp": saved_alert["timestamp"],
                        "image": saved_alert["image"],
                        "lat": saved_alert["lat"],
                        "lon": saved_alert["lon"]
                    })

            self.latest_frames[cam_id] = frame

        except Exception as e:
            logger.error(f"[Camera Error {cam_id}] {e}")

    def run(self):

        logger.info("[Worker] Processing loop started")

        while self.running:

            for cam_id, cam in list(self.cameras.items()):
                self.process_camera(cam_id, cam)

            time.sleep(self.loop_delay)