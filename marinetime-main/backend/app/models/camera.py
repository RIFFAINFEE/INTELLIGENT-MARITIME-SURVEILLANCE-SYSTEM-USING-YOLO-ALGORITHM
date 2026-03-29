from pydantic import BaseModel
from typing import List


class Camera(BaseModel):

    id: str
    name: str
    url: str
    allowed_classes: List[int] = []