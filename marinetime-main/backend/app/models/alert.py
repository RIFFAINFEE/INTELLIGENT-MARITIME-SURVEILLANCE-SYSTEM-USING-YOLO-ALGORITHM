from pydantic import BaseModel
from datetime import datetime


class Alert(BaseModel):

    camera_id: str
    zone_id: str
    object_id: str
    timestamp: datetime
    snapshot: str