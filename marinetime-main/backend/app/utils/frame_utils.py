import cv2
import base64


def resize(frame, width=640):

    h, w = frame.shape[:2]

    ratio = width / w

    return cv2.resize(frame, (width, int(h * ratio)))


def encode_frame(frame):

    _, buffer = cv2.imencode(".jpg", frame)

    return base64.b64encode(buffer).decode("utf-8")