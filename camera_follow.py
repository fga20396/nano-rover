# camera_follow.py
import cv2
import numpy as np
import socket
import time

HOST = '127.0.0.1'
PORT = 8003

def process_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([100, 150, 0]), np.array([140, 255, 255]))
    M = cv2.moments(mask)
    if M["m00"] > 0:
        cx = int(M["m10"] / M["m00"])
        err = cx - frame.shape[1] // 2
        turn = err / (frame.shape[1] // 2)
        return 0.5 + turn, 0.5 - turn
    else:
        return 0.0, 0.0

def connect():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((HOST, PORT))
            print("[Camera] Connected to controller")
            return sock
        except Exception as e:
            print(f"[Camera] Connection failed: {e}")
            time.sleep(2)

def run_camera_follower():
    cap = cv2.VideoCapture(0)
    sock = connect()

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        left, right = process_frame(frame)
        msg = f"{left},{right}"
        try:
            sock.sendall(msg.encode())
        except Exception as e:
            print(f"[Camera] Lost connection: {e}")
            sock.close()
            sock = connect()

if __name__ == "__main__":
    run_camera_follower()
