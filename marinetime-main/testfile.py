import cv2

# url = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()

    if not ret:
        print("failed")
        break

    cv2.imshow("test", frame)

    if cv2.waitKey(1) == 27:
        break