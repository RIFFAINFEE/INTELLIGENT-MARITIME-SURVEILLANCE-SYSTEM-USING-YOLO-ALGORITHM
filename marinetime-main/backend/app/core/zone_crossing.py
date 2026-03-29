from shapely.geometry import Point, Polygon
import time


class ZoneCrossingEngine:

    def __init__(self):

        # zone_id -> polygon
        self.zones = {}

        # track_id -> {zone_id: inside/outside}
        self.history = {}

        # event cooldown memory
        self.last_event = {}

        # seconds to suppress duplicate events
        self.event_cooldown = 1.5

    # -------------------------------------------------
    # Update Zones
    # -------------------------------------------------

    def update_zones(self, zones):

        """
        zones format:
        [
            {
                "id": "zone1",
                "points": [[x,y], [x,y], ...]
            }
        ]
        """

        self.zones = {}

        for z in zones:

            zone_id = z["id"]
            points = z["points"]

            self.zones[zone_id] = Polygon(points)

    # -------------------------------------------------
    # Check Zone Crossing
    # -------------------------------------------------

    def check(self, tracked_objects):

        events = []

        if not self.zones:
            return events

        processed_tracks = set()

        active_tracks = set()

        for obj in tracked_objects:

            track_id = obj["id"]

            active_tracks.add(track_id)

            # prevent duplicate tracker outputs
            if track_id in processed_tracks:
                continue

            processed_tracks.add(track_id)

            x1, y1, x2, y2 = obj["bbox"]

            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            point = Point(cx, cy)

            if track_id not in self.history:
                self.history[track_id] = {}

            for zone_id, polygon in self.zones.items():

                inside = polygon.contains(point)

                prev = self.history[track_id].get(zone_id)

                if prev is None:
                    self.history[track_id][zone_id] = inside
                    continue

                event_type = None

                if prev is False and inside is True:
                    event_type = "ZONE_ENTRY"

                elif prev is True and inside is False:
                    event_type = "ZONE_EXIT"

                if event_type:

                    key = f"{track_id}_{zone_id}_{event_type}"
                    now = time.time()

                    last = self.last_event.get(key)

                    # block duplicate events
                    if last and (now - last) < self.event_cooldown:
                        continue

                    self.last_event[key] = now

                    events.append({
                        "type": event_type,
                        "zone_id": zone_id,
                        "object": obj
                    })

                self.history[track_id][zone_id] = inside

        # cleanup old tracker history
        dead_tracks = set(self.history.keys()) - active_tracks

        for track_id in dead_tracks:
            del self.history[track_id]

        return events