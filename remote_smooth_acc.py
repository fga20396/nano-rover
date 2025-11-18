import pygame
import time
from adafruit_motorkit import MotorKit

# Initialize MotorKit
kit = MotorKit()

# Motors: left side (motor1, motor2), right side (motor3, motor4)
left_front = kit.motor1
left_back = kit.motor2
right_front = kit.motor3
right_back = kit.motor4

# Dead zone threshold
DEAD_ZONE = 0.1
STOP_BUTTON_INDEX = 0  # Emergency stop button index
ACCEL_STEP = 0.05      # Speed change per update
UPDATE_INTERVAL = 0.05 # Loop delay

# Current speeds for smooth acceleration
current_left_speed = 0.0
current_right_speed = 0.0

def apply_dead_zone(value, threshold=DEAD_ZONE):
    return value if abs(value) > threshold else 0.0

def set_motor_throttle(motor, speed):
    speed = max(min(speed, 1.0), -1.0)
    motor.throttle = speed

def set_side_speed(left_speed, right_speed):
    set_motor_throttle(left_front, left_speed)
    set_motor_throttle(left_back, left_speed)
    set_motor_throttle(right_front, right_speed)
    set_motor_throttle(right_back, right_speed)

def stop_motors():
    for motor in [left_front, left_back, right_front, right_back]:
        motor.throttle = 0

def smooth_update(current, target, step=ACCEL_STEP):
    if abs(target - current) < step:
        return target
    return current + step if target > current else current - step

# Initialize Pygame and Joystick
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise Exception("No joystick detected!")

joystick = pygame.joystick.Joystick(0)
joystick.init()

try:
    print("Joystick control started. Press Ctrl+C to exit.")
    while True:
        pygame.event.pump()

        # Emergency stop button
        if joystick.get_button(STOP_BUTTON_INDEX):
            print("Emergency stop triggered!")
            stop_motors()
            current_left_speed = 0.0
            current_right_speed = 0.0
            time.sleep(0.1)
            continue

        # Read joystick axes
        forward_backward = -joystick.get_axis(1)  # Invert for natural forward
        turn = joystick.get_axis(0)

        # Apply dead zone
        forward_backward = apply_dead_zone(forward_backward)
        turn = apply_dead_zone(turn)

        # Calculate target speeds
        target_left_speed = max(min(forward_backward + turn, 1.0), -1.0)
        target_right_speed = max(min(forward_backward - turn, 1.0), -1.0)

        # Smooth acceleration/deceleration
        current_left_speed = smooth_update(current_left_speed, target_left_speed)
        current_right_speed = smooth_update(current_right_speed, target_right_speed)

        # Apply speeds
        set_side_speed(current_left_speed, current_right_speed)

        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:
    print("Stopping robot.")
    stop_motors()
    pygame.quit()
  
