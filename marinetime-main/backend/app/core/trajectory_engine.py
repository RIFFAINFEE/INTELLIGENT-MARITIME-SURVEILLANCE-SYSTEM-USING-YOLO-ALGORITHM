from collections import defaultdict, deque


class TrajectoryEngine:

    def __init__(self, max_points=50):

        self.history = defaultdict(lambda: deque(maxlen=max_points))

    def update(self, tracked_objects):

        paths = {}

        for obj in tracked_objects:

            track_id = obj["id"]

            x1,y1,x2,y2 = obj["bbox"]

            cx = int((x1+x2)/2)
            cy = int((y1+y2)/2)

            self.history[track_id].append((cx,cy))

            paths[track_id] = list(self.history[track_id])

        return paths