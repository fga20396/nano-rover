# controller.py
import socket
import threading
import time

JOYSTICK_PORT = 8002
CAMERA_PORT = 8003
MOTOR_PORT = 8001
HOST = '0.0.0.0'

latest_joystick = None
latest_camera = None

def listener(port, update_func, name):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((HOST, port))
                s.listen(1)
                print(f"[{name}] Listening on port {port}")
                conn, addr = s.accept()
                with conn:
                    print(f"[{name}] Connected: {addr}")
                    conn.settimeout(5)
                    while True:
                        try:
                            data = conn.recv(1024)
                            if not data:
                                break
                            update_func(data.decode().strip())
                        except socket.timeout:
                            print(f"[{name}] Timeout")
                            break
                        except Exception as e:
                            print(f"[{name}] Error:", e)
                            break
        except Exception as e:
            print(f"[{name}] Listener error: {e}")
            time.sleep(2)

def update_joystick(data):
    global latest_joystick
    latest_joystick = (data, time.time())

def update_camera(data):
    global latest_camera
    latest_camera = (data, time.time())

def send_to_motor(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect(('127.0.0.1', MOTOR_PORT))
            s.sendall(data.encode())
    except Exception as e:
        print("[Controller] Motor send failed:", e)

def run_controller():
    threading.Thread(target=listener, args=(JOYSTICK_PORT, update_joystick, "Joystick"), daemon=True).start()
    threading.Thread(target=listener, args=(CAMERA_PORT, update_camera, "Camera"), daemon=True).start()

    while True:
        time.sleep(0.1)
        now = time.time()
        command = None

        if latest_joystick and now - latest_joystick[1] < 1:
            command = latest_joystick[0]
        elif latest_camera and now - latest_camera[1] < 1:
            command = latest_camera[0]

        if command:
            send_to_motor(command)

if __name__ == "__main__":
    run_controller()
