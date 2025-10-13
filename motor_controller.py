# motor_controller.py
from adafruit_motorkit import MotorKit
import socket
import time

kit = MotorKit()
HOST = '0.0.0.0'
PORT = 8001

def drive(left_speed, right_speed):
    kit.motor1.throttle = left_speed
    kit.motor2.throttle = left_speed
    kit.motor3.throttle = right_speed
    kit.motor4.throttle = right_speed

def stop():
    for motor in [kit.motor1, kit.motor2, kit.motor3, kit.motor4]:
        motor.throttle = 0

def run_motor_server():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((HOST, PORT))
                s.listen(1)
                print(f"[Motor] Listening on port {PORT}...")
                conn, addr = s.accept()
                with conn:
                    print(f"[Motor] Connected by {addr}")
                    conn.settimeout(5)
                    while True:
                        try:
                            data = conn.recv(1024)
                            if not data:
                                break
                            cmd = data.decode().strip()
                            if cmd == "STOP":
                                stop()
                            else:
                                left, right = map(float, cmd.split(","))
                                drive(left, right)
                        except socket.timeout:
                            print("[Motor] Connection timeout")
                            break
                        except Exception as e:
                            print("[Motor] Error:", e)
                            stop()
                            break
        except Exception as e:
            print("[Motor] Server error:", e)
            time.sleep(2)

if __name__ == "__main__":
    run_motor_server()
