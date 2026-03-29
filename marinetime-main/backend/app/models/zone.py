from pydantic import BaseModel
from typing import List, Optional


# --------------------------------------------------
# Create Zone
# --------------------------------------------------

class ZoneCreate(BaseModel):

    id: str
    camera_id: str
    name: str

    # normalized polygon points (0-1)
    points: List[List[float]]

    # classes that trigger alerts
    # example: ["ship","boat","person"]
    allowed_classes: Optional[List[str]] = []


# --------------------------------------------------
# Update Zone
# --------------------------------------------------

class ZoneUpdate(BaseModel):

    name: Optional[str] = None

    # update polygon
    points: Optional[List[List[float]]] = None

    # update allowed classes
    allowed_classes: Optional[List[str]] = None