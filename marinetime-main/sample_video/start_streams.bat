@echo off
echo Starting virtual IP cameras...

@REM REM Camera 1
@REM start "cam1" ffmpeg -re -stream_loop -1 -i video1.mp4 ^
@REM -c:v libx264 ^
@REM -preset veryfast ^
@REM -tune zerolatency ^
@REM -r 30 ^
@REM -g 30 ^
@REM -b:v 2M ^
@REM -maxrate 2M ^
@REM -bufsize 4M ^
@REM -rtsp_transport tcp ^
@REM -f rtsp rtsp://localhost:8554/cam1

@REM REM Camera 2
@REM start "cam2" ffmpeg -re -stream_loop -1 -i video5.mp4 ^
@REM -c:v libx264 ^
@REM -preset veryfast ^
@REM -tune zerolatency ^
@REM -r 30 ^
@REM -g 30 ^
@REM -b:v 2M ^
@REM -maxrate 2M ^
@REM -bufsize 4M ^
@REM -rtsp_transport tcp ^
@REM -f rtsp rtsp://localhost:8554/cam2

@REM REM Camera 3
@REM start "cam3" ffmpeg -re -stream_loop -1 -i video6.mp4 ^
@REM -c:v libx264 ^
@REM -preset veryfast ^
@REM -tune zerolatency ^
@REM -r 30 ^
@REM -g 30 ^
@REM -b:v 2M ^
@REM -maxrate 2M ^
@REM -bufsize 4M ^
@REM -rtsp_transport tcp ^
@REM -f rtsp rtsp://localhost:8554/cam3

@REM REM Camera 4
@REM start "cam4" ffmpeg -re -stream_loop -1 -i video7.mp4 ^
@REM -c:v libx264 ^
@REM -preset veryfast ^
@REM -tune zerolatency ^
@REM -r 30 ^
@REM -g 30 ^
@REM -b:v 2M ^
@REM -maxrate 2M ^
@REM -bufsize 4M ^
@REM -rtsp_transport tcp ^
@REM -f rtsp rtsp://localhost:8554/cam4

@REM REM Camera 5 (HLS Source)
@REM start "cam5" ffmpeg -re -i "https://2-fss-2.streamhoster.com/pl_126/200612-2266250-1/chunklist.m3u8" ^
@REM -c:v libx264 ^
@REM -preset veryfast ^
@REM -tune zerolatency ^
@REM -r 30 ^
@REM -g 30 ^
@REM -b:v 2M ^
@REM -maxrate 2M ^
@REM -bufsize 4M ^
@REM -rtsp_transport tcp ^
@REM -f rtsp rtsp://localhost:8554/cam5

REM Camera 6
start "cam6" ffmpeg -re -stream_loop -1 -i video12.mp4 ^
-c:v libx264 ^
-preset veryfast ^
-tune zerolatency ^
-r 30 ^
-g 30 ^
-b:v 2M ^
-maxrate 2M ^
-bufsize 4M ^
-rtsp_transport tcp ^
-f rtsp rtsp://localhost:8554/cam6

echo.
echo Cameras started.
echo.

echo RTSP Streams:
echo rtsp://localhost:8554/cam1
echo rtsp://localhost:8554/cam2
echo rtsp://localhost:8554/cam3
echo rtsp://localhost:8554/cam4
echo rtsp://localhost:8554/cam5
echo rtsp://localhost:8554/cam6

echo.
echo WebRTC preview (MediaMTX):
echo http://localhost:8889/cam1
echo http://localhost:8889/cam2
echo http://localhost:8889/cam3
echo http://localhost:8889/cam4
echo http://localhost:8889/cam5
echo http://localhost:8889/cam6

pause