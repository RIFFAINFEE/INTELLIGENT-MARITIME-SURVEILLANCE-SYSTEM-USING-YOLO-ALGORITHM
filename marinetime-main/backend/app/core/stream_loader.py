import cv2

class StreamLoader:

    def __init__(self, url):
        self.url = url
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)

    def read(self):
        if not self.cap:
            return None

        ret, frame = self.cap.read()

        if not ret:
            return None

        return frame

    def release(self):
        if self.cap:
            self.cap.release()