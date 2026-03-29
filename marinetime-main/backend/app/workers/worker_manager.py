from app.workers.stream_worker import StreamWorker


class WorkerManager:

    def __init__(self):

        # Main stream worker
        self.worker = StreamWorker()

        # Stores latest detections from YOLO
        # {camera_id : [ {bbox,label,conf}, ... ]}
        self.worker.latest_detections = {}

        # start worker thread immediately
        self.worker.start()

    # --------------------------------------------------
    # Start Camera Stream
    # --------------------------------------------------

    def start_stream(self, camera_id, url, allowed_classes=None):

        if camera_id in self.worker.cameras:
            return

        self.worker.add_camera(
            camera_id,
            url,
            allowed_classes
        )

    # --------------------------------------------------
    # Stop Camera Stream
    # --------------------------------------------------

    def stop_stream(self, camera_id):

        if camera_id not in self.worker.cameras:
            return

        self.worker.remove_camera(camera_id)

        # cleanup stored data
        if camera_id in self.worker.latest_detections:
            del self.worker.latest_detections[camera_id]

        if camera_id in self.worker.latest_frames:
            del self.worker.latest_frames[camera_id]

    # --------------------------------------------------
    # List Active Streams
    # --------------------------------------------------

    def list_streams(self):

        streams = []

        for cam_id in self.worker.cameras:

            streams.append({
                "camera_id": cam_id
            })

        return streams


# Singleton manager
manager = WorkerManager()