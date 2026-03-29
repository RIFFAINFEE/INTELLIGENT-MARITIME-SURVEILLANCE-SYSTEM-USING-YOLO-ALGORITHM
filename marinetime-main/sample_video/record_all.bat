@echo off
echo Starting 15-minute recording for all cameras...

REM Camera 1 (MJPEG stream)
start ffmpeg -y -t 900 -i "http://62.110.217.34:8080/mjpg/video.mjpg" -c:v libx264 -pix_fmt yuv420p video1.mp4

REM Camera 2 (snapshot camera)
start ffmpeg -y -loop 1 -framerate 5 -t 900 -i "http://185.97.122.32:8080/record/current.jpg" -c:v libx264 -pix_fmt yuv420p video2.mp4

REM Camera 3
start ffmpeg -y -loop 1 -framerate 5 -t 900 -i "http://80.32.125.254:8080/record/current.jpg" -c:v libx264 -pix_fmt yuv420p video3.mp4

REM Camera 4
start ffmpeg -y -loop 1 -framerate 5 -t 900 -i "http://185.78.0.10:8082/record/current.jpg" -c:v libx264 -pix_fmt yuv420p video4.mp4

REM Camera 5 (MJPEG stream)
start ffmpeg -y -t 900 -i "http://217.7.227.83:8080/cgi-bin/faststream.jpg?stream=full&fps=1" -c:v libx264 -pix_fmt yuv420p video5.mp4

REM Camera 6 (MJPEG stream)
start ffmpeg -y -t 900 -i "http://212.139.127.182:8080/mjpg/video.mjpg" -c:v libx264 -pix_fmt yuv420p video6.mp4

REM Camera 7 (snapshot camera)
start ffmpeg -y -loop 1 -framerate 5 -t 900 -i "http://194.71.159.17/axis-cgi/jpg/image.cgi?camera=1" -c:v libx264 -pix_fmt yuv420p video7.mp4

echo Recording started. All cameras will record for 15 minutes.
pause