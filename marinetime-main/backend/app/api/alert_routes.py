from fastapi import APIRouter
from app.core.alert_storage import alert_storage

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"]
)

# --------------------------------------------------
# Get All Alerts
# --------------------------------------------------

@router.get("/")
def get_alerts():

    alerts = alert_storage.list()

    print("\n================ ALERT API =================")
    print(f"[ALERT API] Total alerts in memory: {len(alerts)}")
    print("[ALERT API] Alerts:", alerts)
    print("============================================\n")

    return {
        "alerts": alerts
    }


# --------------------------------------------------
# Get Alerts By Camera
# --------------------------------------------------

@router.get("/camera/{camera_id}")
def get_camera_alerts(camera_id: str):

    alerts = alert_storage.by_camera(camera_id)

    print("\n================ CAMERA ALERT API =================")
    print(f"[ALERT API] Camera: {camera_id}")
    print(f"[ALERT API] Alerts found: {len(alerts)}")
    print("[ALERT API] Alerts:", alerts)
    print("===================================================\n")

    return {
        "camera_id": camera_id,
        "alerts": alerts
    }