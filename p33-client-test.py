"""
Connects to the motor server via TCP.
Reads joystick axis input using evdev.
Sends JSON commands with action: "run" and speed from -1.0 to 1.0.
Handles connection errors and automatically reconnects.
Prints acknowledgment from the server.

pip install evdev

Common Xbox Axis Mappings (evdev):

Axis Name      evdev Code    Typical Use
============================================
Left Stick     YABS_Y        Forward/backward
Right Stick    YABS_RY       Second motor or alternate control

"""

import socket
import json
import time
from evdev import InputDevice, ecodes, list_devices

# Find Xbox joystick device
joystick = None
for dev_path in list_devices():
    dev = InputDevice(dev_path)
    if 'xbox' in dev.name.lower() or 'gamepad' in dev.name.lower():
        joystick = dev
        break

if joystick is None:
    raise RuntimeError("No Xbox joystick or gamepad device found.")

print(f"Using joystick: {joystick.name} at {joystick.path}")

# TCP server configuration
HOST = '127.0.0.1'  # Change to server IP if needed
PORT = 65432

# Axis mapping for Xbox controller
AXIS_MOTOR1 = ecodes.ABS_Y   # Left stick Y
AXIS_MOTOR2 = ecodes.ABS_RY  # Right stick Y

# Normalize axis value to [-1.0, 1.0]
def normalize(value, min_val=0, max_val=255):
    return (value - min_val) / (max_val - min_val) * 2 - 1

# Connect to server with retry
def connect_to_server():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            print("Connected to motor server.")
            return s
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 2 seconds...")
            time.sleep(2)

# Main loop
sock = connect_to_server()
axis_values = {AXIS_MOTOR1: 128, AXIS_MOTOR2: 128}  # Default mid-range

try:
    for event in joystick.read_loop():
        if event.type == ecodes.EV_ABS:
            axis_values[event.code] = event.value

            speed1 = normalize(axis_values.get(AXIS_MOTOR1, 128), 0, 255)
            speed2 = normalize(axis_values.get(AXIS_MOTOR2, 128), 0, 255)

            command = {
                "motor1": {"action": "run", "speed": round(speed1, 2)},
                "motor2": {"action": "run", "speed": round(speed2, 2)}
            }

            while True:
                try:
                    sock.sendall(json.dumps(command).encode())
                    ack = sock.recv(1024)
                    print(f"ACK: {ack.decode()}")
                    break
                except Exception as e:
                    print(f"Error sending command: {e}. Reconnecting...")
                    sock.close()
                    sock = connect_to_server()
except KeyboardInterrupt:
    print("Client terminated by user.")
    sock.close()
``
