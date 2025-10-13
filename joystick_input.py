# joystick_input.py
from evdev import InputDevice, ecodes
import socket
import time

JOYSTICK_DEVICE = '/dev/input/event0'
HOST = '192.168.1.42'  # Static IP of Raspberry Pi
PORT = 8002

def map_axis(value):
    return round(value / 32767.0, 2)

def connect():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((HOST, PORT))
            print("[Joystick] Connected to controller")
            return sock
        except Exception as e:
            print(f"[Joystick] Connection failed: {e}")
            time.sleep(2)

def run_joystick_client():
    dev = InputDevice(JOYSTICK_DEVICE)
    print(f"[Joystick] Using device: {dev.name}")

    sock = connect()
    x_axis, y_axis = 0, 0

    for event in dev.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_X:
                x_axis = map_axis(event.value)
            elif event.code == ecodes.ABS_Y:
                y_axis = map_axis(event.value)

            left_speed = y_axis + x_axis
            right_speed = y_axis - x_axis
            msg = f"{left_speed},{right_speed}"

            try:
                sock.sendall(msg.encode())
            except Exception as e:
                print(f"[Joystick] Lost connection: {e}")
                sock.close()
                sock = connect()

if __name__ == "__main__":
    run_joystick_client()
