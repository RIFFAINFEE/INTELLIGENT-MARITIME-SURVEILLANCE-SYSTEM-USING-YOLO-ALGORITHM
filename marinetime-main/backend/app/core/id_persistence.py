import time


class IDPersistence:

    def __init__(self, ttl=10):

        self.last_seen = {}

        self.ttl = ttl

    def update(self, tracked):

        now = time.time()

        valid = []

        for obj in tracked:

            track_id = obj["id"]

            self.last_seen[track_id] = now

            valid.append(obj)

        # remove old IDs
        expired = [
            k for k,v in self.last_seen.items()
            if now-v > self.ttl
        ]

        for k in expired:
            del self.last_seen[k]

        return valid