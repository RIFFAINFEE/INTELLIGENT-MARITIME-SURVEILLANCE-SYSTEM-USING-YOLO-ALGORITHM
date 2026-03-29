from fastapi import APIRouter, HTTPException

from app.models.zone import ZoneCreate, ZoneUpdate
from app.core.zone_store import zone_store

router = APIRouter(prefix="/zone", tags=["zones"])


@router.post("/create")

def create_zone(zone: ZoneCreate):

    if zone_store.get(zone.id):
        raise HTTPException(400, "Zone already exists")

    zone_store.create(zone.dict())

    return {"status": "created"}


@router.put("/{zone_id}")

def update_zone(zone_id: str, data: ZoneUpdate):

    zone = zone_store.update(zone_id, data.dict(exclude_none=True))

    if not zone:
        raise HTTPException(404, "Zone not found")

    return zone


@router.delete("/{zone_id}")

def delete_zone(zone_id: str):

    zone_store.delete(zone_id)

    return {"status": "deleted"}


@router.get("/list")

def list_zones():

    return zone_store.list()


@router.get("/camera/{camera_id}")

def zones_by_camera(camera_id: str):

    return zone_store.by_camera(camera_id)


@router.get("/{zone_id}")

def get_zone(zone_id: str):

    zone = zone_store.get(zone_id)

    if not zone:
        raise HTTPException(404, "Zone not found")

    return zone