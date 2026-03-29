from shapely.geometry import Point, Polygon


class ZoneEngine:

    def __init__(self):

        # zone_id -> polygon
        self.zones = {}

    # -------------------------------------------------
    # Update Zones
    # -------------------------------------------------

    def update_zones(self, zones):

        """
        zones format expected:
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
    # Check Objects Inside Zones
    # -------------------------------------------------

    def check(self, objects):

        events = []

        if not self.zones:
            return events

        for obj in objects:

            x1, y1, x2, y2 = obj["bbox"]

            # object center
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            point = Point(cx, cy)

            for zone_id, polygon in self.zones.items():

                if polygon.contains(point):

                    events.append(
                        {
                            "zone_id": zone_id,
                            "object": obj,
                        }
                    )

        return events