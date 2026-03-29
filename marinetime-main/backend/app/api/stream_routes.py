import cv2
import time
import numpy as np

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from app.workers.worker_manager import manager
from app.core.zone_store import zone_store


router = APIRouter(
    prefix="/stream",
    tags=["stream"]
)


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class StartStreamRequest(BaseModel):

    id: str
    url: str
    allowed_classes: Optional[List[str]] = []


# --------------------------------------------------
# RAW FRAME GENERATOR
# --------------------------------------------------

def generate(camera_id: str):

    worker = manager.worker

    while True:

        frame = worker.latest_frames.get(camera_id)

        if frame is None:
            time.sleep(0.03)
            continue

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes() +
            b"\r\n"
        )


# --------------------------------------------------
# FRAME GENERATOR WITH ZONES
# --------------------------------------------------

def generate_with_zones(camera_id: str):

    worker = manager.worker

    while True:

        frame = worker.latest_frames.get(camera_id)

        if frame is None:
            time.sleep(0.03)
            continue

        frame_copy = frame.copy()

        zones = zone_store.by_camera(camera_id)

        h, w = frame_copy.shape[:2]

        for zone in zones:

            points = zone["points"]

            pixel_points = [
                [int(p[0] * w), int(p[1] * h)]
                for p in points
            ]

            pts_np = np.array(pixel_points, np.int32).reshape((-1, 1, 2))

            cv2.polylines(
                frame_copy,
                [pts_np],
                True,
                (0, 0, 255),
                2
            )

            x, y = pixel_points[0]

            cv2.putText(
                frame_copy,
                zone["name"],
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        ret, buffer = cv2.imencode(".jpg", frame_copy)

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes() +
            b"\r\n"
        )


# --------------------------------------------------
# YOLO DETECTION PREVIEW
# --------------------------------------------------

def generate_yolo(camera_id: str):

    worker = manager.worker

    while True:

        frame = worker.latest_frames.get(camera_id)

        if frame is None:
            time.sleep(0.03)
            continue

        frame_copy = frame.copy()

        detections = worker.latest_detections.get(camera_id, [])

        for det in detections:

            try:

                x1, y1, x2, y2 = det["bbox"]

                # FIXED KEYS
                label = det.get("name", "obj")
                conf = det.get("score", 0)

                cv2.rectangle(
                    frame_copy,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame_copy,
                    f"{label} {conf:.2f}",
                    (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

            except Exception:
                continue

        ret, buffer = cv2.imencode(".jpg", frame_copy)

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes() +
            b"\r\n"
        )


# --------------------------------------------------
# RAW PREVIEW
# --------------------------------------------------

@router.get("/preview/{camera_id}")
def preview(camera_id: str):

    worker = manager.worker

    if camera_id not in worker.latest_frames:
        worker.latest_frames[camera_id] = None

    return StreamingResponse(
        generate(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# --------------------------------------------------
# PREVIEW WITH ZONES
# --------------------------------------------------

@router.get("/preview_with_zones/{camera_id}")
def preview_with_zones(camera_id: str):

    worker = manager.worker

    if camera_id not in worker.latest_frames:
        worker.latest_frames[camera_id] = None

    return StreamingResponse(
        generate_with_zones(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# --------------------------------------------------
# YOLO DETECTION PREVIEW
# --------------------------------------------------

@router.get("/yolo_preview/{camera_id}")
def yolo_preview(camera_id: str):

    worker = manager.worker

    if camera_id not in worker.latest_frames:
        worker.latest_frames[camera_id] = None

    return StreamingResponse(
        generate_yolo(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# --------------------------------------------------
# START STREAM
# --------------------------------------------------

@router.post("/start")
def start_stream(data: StartStreamRequest):

    manager.start_stream(
        camera_id=data.id,
        url=data.url,
        allowed_classes=data.allowed_classes
    )

    return {
        "status": "started",
        "camera": data.id
    }


# --------------------------------------------------
# STOP STREAM
# --------------------------------------------------

@router.post("/stop/{camera_id}")
def stop_stream(camera_id: str):

    manager.stop_stream(camera_id)

    return {
        "status": "stopped",
        "camera": camera_id
    }


# --------------------------------------------------
# LIST STREAMS
# --------------------------------------------------

@router.get("/list")
def list_streams():

    return {
        "streams": manager.list_streams()
    }