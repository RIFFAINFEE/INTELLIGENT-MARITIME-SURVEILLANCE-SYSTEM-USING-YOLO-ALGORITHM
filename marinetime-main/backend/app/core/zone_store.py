from threading import Lock

class ZoneStore:

    def __init__(self):
        self.zones = {}
        self.lock = Lock()

    def create(self, zone):

        with self.lock:

            self.zones[zone["id"]] = zone

    def update(self, zone_id, data):

        with self.lock:

            if zone_id not in self.zones:
                return None

            if "name" in data:
                self.zones[zone_id]["name"] = data["name"]

            if "points" in data:
                self.zones[zone_id]["points"] = data["points"]

            return self.zones[zone_id]

    def delete(self, zone_id):

        with self.lock:

            if zone_id in self.zones:
                del self.zones[zone_id]

    def get(self, zone_id):

        return self.zones.get(zone_id)

    def list(self):

        return list(self.zones.values())

    def by_camera(self, camera_id):

        return [
            z for z in self.zones.values()
            if z["camera_id"] == camera_id
        ]


zone_store = ZoneStore()