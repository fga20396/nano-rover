import pygame
import time
from adafruit_motorkit import MotorKit

# Initialize MotorKit (I2C address defaults to 0x60)
kit = MotorKit()

# Motors: left side (motor1, motor2), right side (motor3, motor4)
left_front = kit.motor1
left_back = kit.motor2
right_front = kit.motor3
right_back = kit.motor4

# Dead zone threshold
DEAD_ZONE = 0.1
STOP_BUTTON_INDEX = 0  # Change based on your joystick layout

def apply_dead_zone(value, threshold=DEAD_ZONE):
    return value if abs(value) > threshold else 0.0

def set_motor_throttle(motor, speed):
    # Clamp speed between -1.0 and 1.0
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
            time.sleep(0.1)
            continue

        # Read joystick axes
        forward_backward = -joystick.get_axis(1)  # Invert for natural forward
        turn = joystick.get_axis(0)

        # Apply dead zone
        forward_backward = apply_dead_zone(forward_backward)
        turn = apply_dead_zone(turn)

        # Mix turning with forward/backward
        left_speed = forward_backward + turn
        right_speed = forward_backward - turn

        # Clamp values between -1.0 and 1.0
        left_speed = max(min(left_speed, 1.0), -1.0)
        right_speed = max(min(right_speed, 1.0), -1.0)

        # Set speeds for both motors on each side
        set_side_speed(left_speed, right_speed)

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopping robot.")
    stop_motors()
    pygame.quit()
