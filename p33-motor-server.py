import socket
import json
import logging
import signal
import sys
from adafruit_motorkit import MotorKit
from adafruit_motor import motor

# Setup logging
logging.basicConfig(
    filename='motor_control.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize MotorKit
kit = MotorKit()

# Secure motors before listening
def secure_motors():
    kit.motor1.throttle = 0
    kit.motor2.throttle = 0
    logging.info("Motors secured (stopped).")

# Graceful shutdown handler
def shutdown_handler(signum, frame):
    logging.info(f"Received shutdown signal ({signum}). Cleaning up...")
    secure_motors()
    logging.info("Shutdown complete.")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

secure_motors()

# TCP Server Configuration
HOST = '0.0.0.0'
PORT = 65432

def handle_command(data):
    try:
        command = json.loads(data)
        responses = {}

        for motor_id in ["motor1", "motor2"]:
            if motor_id in command:
                motor_cmd = command[motor_id]
                action = motor_cmd.get("action")
                speed = motor_cmd.get("speed", 0)

                motor_obj = kit.motor1 if motor_id == "motor1" else kit.motor2

                if action == "run":
                    speed = max(min(speed, 1.0), -1.0)
                    motor_obj.throttle = speed
                elif action == "stop":
                    motor_obj.throttle = 0
                else:
                    raise ValueError(f"Invalid action for {motor_id}: {action}")

                responses[motor_id] = {"status": "ok", "action": action, "speed": speed}
                logging.info(f"{motor_id} executed: {motor_cmd}")

        return responses if responses else {"status": "error", "message": "No valid motor commands found"}

    except Exception as e:
        logging.error(f"Error handling command: {data} - {e}")
        return {"status": "error", "message": str(e)}

def start_server():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((HOST, PORT))
                s.listen()
                logging.info(f"Server listening on {HOST}:{PORT}")

                while True:
                    conn, addr = s.accept()
                    logging.info(f"Connection established with {addr}")
                    with conn:
                        while True:
                            try:
                                data = conn.recv(1024)
                                if not data:
                                    logging.info(f"Connection closed by {addr}")
                                    break
                                response = handle_command(data.decode())
                                conn.sendall(json.dumps(response).encode())
                            except Exception as e:
                                logging.error(f"Error during communication with {addr}: {e}")
                                break
        except Exception as e:
            logging.critical(f"Server error: {e}. Restarting server...")
            continue

if __name__ == "__main__":
    start_server()
