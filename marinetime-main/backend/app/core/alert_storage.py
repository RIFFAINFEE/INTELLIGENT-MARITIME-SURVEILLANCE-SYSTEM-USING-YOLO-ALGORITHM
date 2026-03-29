import os
import cv2
import time
import sqlite3


class AlertStorage:

    def __init__(self):

        self.base_path = "alerts"
        os.makedirs(self.base_path, exist_ok=True)

        self.db_path = "alerts.db"

        self.init_db()

        print("[ALERT STORAGE] SQLite initialized")

    # --------------------------------------------------
    # Initialize Database
    # --------------------------------------------------

    def init_db(self):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT,
            zone_id TEXT,
            object_id INTEGER,
            object_name TEXT,
            timestamp INTEGER,
            image TEXT,
            lat REAL,
            lon REAL
        )
        """)

        conn.commit()
        conn.close()

    # --------------------------------------------------
    # Save Alert
    # --------------------------------------------------

    def save(self, frame, camera_id, zone_id, object_id, object_name=None, lat=None, lon=None):

        timestamp = int(time.time())

        cam_folder = os.path.join(self.base_path, camera_id)
        os.makedirs(cam_folder, exist_ok=True)

        filename = f"{zone_id}_{object_id}_{timestamp}.jpg"
        filepath = os.path.join(cam_folder, filename)

        cv2.imwrite(filepath, frame)

        print(f"[ALERT STORAGE] Image saved -> {filepath}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO alerts (camera_id, zone_id, object_id, object_name, timestamp, image, lat, lon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (camera_id, zone_id, object_id, object_name, timestamp, filepath, lat, lon))

        conn.commit()
        conn.close()

        print("[ALERT STORAGE] Alert stored in database")

        return {
            "camera_id": camera_id,
            "zone_id": zone_id,
            "object_id": object_id,
            "object": object_name,
            "timestamp": timestamp,
            "image": filepath,
            "lat": lat,
            "lon": lon
        }

    # --------------------------------------------------
    # Get All Alerts
    # --------------------------------------------------

    def list(self):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT camera_id, zone_id, object_id, object_name, timestamp, image, lat, lon
        FROM alerts
        ORDER BY timestamp DESC
        LIMIT 100
        """)

        rows = cursor.fetchall()

        conn.close()

        alerts = []

        for r in rows:
            alerts.append({
                "camera_id": r[0],
                "zone_id": r[1],
                "object_id": r[2],
                "object": r[3],
                "timestamp": r[4],
                "image": r[5],
                "lat": r[6],
                "lon": r[7]
            })

        print(f"[ALERT STORAGE] Returning {len(alerts)} alerts")

        return alerts

    # --------------------------------------------------
    # Alerts By Camera
    # --------------------------------------------------

    def by_camera(self, camera_id):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT camera_id, zone_id, object_id, object_name, timestamp, image, lat, lon
        FROM alerts
        WHERE camera_id=?
        ORDER BY timestamp DESC
        LIMIT 100
        """, (camera_id,))

        rows = cursor.fetchall()

        conn.close()

        alerts = []

        for r in rows:
            alerts.append({
                "camera_id": r[0],
                "zone_id": r[1],
                "object_id": r[2],
                "object": r[3],
                "timestamp": r[4],
                "image": r[5],
                "lat": r[6],
                "lon": r[7]
            })

        print(f"[ALERT STORAGE] Returning {len(alerts)} alerts for camera {camera_id}")

        return alerts


# Singleton instance
alert_storage = AlertStorage()