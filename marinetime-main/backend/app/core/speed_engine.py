import math
import time


class SpeedEngine:

    def __init__(self):

        self.history = {}

    def update(self, obj):

        track_id = obj["id"]

        x1,y1,x2,y2 = obj["bbox"]

        cx = (x1+x2)/2
        cy = (y1+y2)/2

        now = time.time()

        if track_id not in self.history:

            self.history[track_id] = (cx,cy,now)

            return None

        px,py,pt = self.history[track_id]

        dist = math.sqrt((cx-px)**2 + (cy-py)**2)

        dt = now - pt

        self.history[track_id] = (cx,cy,now)

        if dt == 0:
            return None

        speed = dist/dt

        return speed