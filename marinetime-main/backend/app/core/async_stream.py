# import cv2
# import threading
# import time
# import os

# class AsyncVideoStream:


#     def __init__(self, url):

#         self.url = url
#         self.is_file = os.path.exists(url)

#         self.cap = cv2.VideoCapture(url)

#         self.frame = None
#         self.running = False

#     def start(self):

#         print("[STREAM] Starting stream:", self.url)

#         self.running = True

#         thread = threading.Thread(target=self.update, daemon=True)
#         thread.start()

#         return self

#     def update(self):

#         while self.running:

#             if not self.cap.isOpened():

#                 print("[STREAM] Source not opened. Retrying...")
#                 self.cap.open(self.url)
#                 time.sleep(2)
#                 continue

#             ret, frame = self.cap.read()

#             # ------------------------------
#             # VIDEO END HANDLING (NO LOOP)
#             # ------------------------------

#             if not ret:

#                 if self.is_file:
#                     print("[STREAM] Video finished. Stopping stream.")
#                     self.running = False
#                     break

#                 else:
#                     print("[STREAM] Failed to read frame")
#                     time.sleep(1)
#                     continue

#             self.frame = frame

#     def read(self):

#         return self.frame

#     def stop(self):

#         self.running = False
#         self.cap.release()









import cv2
import threading
import time
import os

class AsyncVideoStream:

    def __init__(self, url):

        self.url = url
        self.is_file = os.path.exists(url)

        self.cap = cv2.VideoCapture(url)

        self.frame = None
        self.running = False

        # detect fps (used to simulate real-time playback for files)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        if self.fps <= 0 or self.fps > 120:
            self.fps = 10

        self.frame_delay = 1.0 / self.fps

    def start(self):

        print("[STREAM] Starting stream:", self.url)
        print("[STREAM] FPS:", self.fps)

        self.running = True

        thread = threading.Thread(target=self.update, daemon=True)
        thread.start()

        return self

    def update(self):

        while self.running:

            if not self.cap.isOpened():

                print("[STREAM] Source not opened. Retrying...")
                self.cap.open(self.url)
                time.sleep(2)
                continue

            ret, frame = self.cap.read()

            # ------------------------------
            # VIDEO END HANDLING (NO LOOP)
            # ------------------------------

            if not ret:

                if self.is_file:

                    print("[STREAM] Video finished. Stopping stream.")

                    self.frame = None
                    self.running = False
                    self.cap.release()
                    break

                else:

                    print("[STREAM] Failed to read frame")
                    time.sleep(1)
                    continue

            self.frame = frame

            # simulate real camera FPS for video files
            if self.is_file:
                time.sleep(self.frame_delay)

    def read(self):

        return self.frame

    def stop(self):

        self.running = False
        self.cap.release()


