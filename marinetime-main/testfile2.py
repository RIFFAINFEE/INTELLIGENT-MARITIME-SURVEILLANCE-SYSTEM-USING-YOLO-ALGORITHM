import cv2

cap = cv2.VideoCapture("rtsp://localhost:8554/cam1")

while True:
    ret, frame = cap.read()

    if not ret:
        print("stream error")
        break

    cv2.imshow("cam1", frame)

    if cv2.waitKey(1) == 27:
        break