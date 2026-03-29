from fastapi import APIRouter
from pydantic import BaseModel

from app.workers.worker_manager import manager

router = APIRouter()


class CameraRequest(BaseModel):

    id: str
    url: str
    allowed_classes: list[int] | None = None


@router.post("/camera/start")
def start_camera(cam: CameraRequest):

    manager.start_stream(cam.id, cam.url, cam.allowed_classes)

    return {"status": "started", "camera": cam.id}


@router.post("/camera/stop")
def stop_camera(cam: CameraRequest):

    manager.stop_stream(cam.id)

    return {"status": "stopped"}


@router.get("/camera/list")
def list_cameras():

    return manager.list_streams()