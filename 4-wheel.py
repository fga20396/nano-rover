import time
import json
from evdev import InputDevice, categorize, ecodes, list_devices
from adafruit_motorkit import MotorKit

# Load calibration data
def load_calibration(filename="joystick_calibration.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Calibration file not found. Please run the calibration program first.")
        exit(1)

# Normalize axis value using calibration data
def normalize(value, axis_cal):
    min_val = axis_cal['min']
    max_val = axis_cal['max']
    center = axis_cal['center']
    if value < center:
        return -((center - value) / (center - min_val))
    else:
        return (value - center) / (max_val - center)

# Find joystick device
def find_joystick():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if 'joystick' in device.name.lower() or 'gamepad' in device.name.lower():
            print(f"Using joystick: {device.name} at {device.path}")
            return device
    raise RuntimeError("No joystick found")

# Main control loop
def main():
    kit = MotorKit()
    joystick = find_joystick()
    calibration = load_calibration()

    forward = 0.0
    turn = 0.0

    for event in joystick.read_loop():
        if event.type == ecodes.EV_ABS:
            axis_code = event.code
            axis_name = ecodes.ABS.get(axis_code, f"ABS_{axis_code}")
            value = event.value

            if axis_name in calibration:
                norm = normalize(value, calibration[axis_name])

                if axis_name == "ABS_Y":  # Forward/backward
                    forward = -norm  # Invert Y axis
                elif axis_name == "ABS_X":  # Left/right
                    turn = norm

                # Differential drive logic
                left_speed = max(min(forward + turn, 1.0), -1.0)
                right_speed = max(min(forward - turn, 1.0), -1.0)

                # Apply to all four motors
                kit.motor1.throttle = left_speed   # Front-left
                kit.motor2.throttle = right_speed  # Front-right
                kit.motor3.throttle = left_speed   # Rear-left
                kit.motor4.throttle = right_speed  # Rear-right

        elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TRIGGER:
            if event.value == 0:  # Button released
                kit.motor1.throttle = 0
                kit.motor2.throttle = 0
                kit.motor3.throttle = 0
                kit.motor4.throttle = 0

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping motors...")
        kit.motor1.throttle = 0
        kit.motor2.throttle = 0
        kit.motor3.throttle = 0
        kit.motor4.throttle = 0
