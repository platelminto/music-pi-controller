import socket
import json
import os
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

load_dotenv()

pi_ip = os.getenv("PI_IP")
pi_port = int(os.getenv("PI_PORT"))


def send_command(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    message = json.dumps(command)
    print(pi_ip, pi_port, message)
    sock.sendto(message.encode(), (pi_ip, pi_port))


def turn_led_on(led_id: int, duration: Optional[float] = None, power_percentage: int = 100):
    if not (0 <= power_percentage <= 100):
        raise ValueError("Power percentage must be between 0 and 100")

    command = {"cmd": "set-led", "pin": led_id, "power": power_percentage}

    send_command(command)

    if duration:
        time.sleep(duration)
        turn_led_off(led_id)


def turn_led_off(led_id):
    command = {"cmd": "set-led", "pin": led_id, "power": 0}

    send_command(command)


def debug_print(message):
    command = {"cmd": "debug-print", "message": message}

    send_command(command)


if __name__ == "__main__":
    led_ids = [18, 23, 24, 25, 8, 7, 1]

    executor = ThreadPoolExecutor()
    executor.submit(turn_led_on, 18, 3, 20)
    executor.submit(turn_led_on, 23, 3, 30)
    executor.submit(turn_led_on, 24, 3, 40)
    executor.submit(turn_led_on, 25, 3, 50)
    executor.submit(turn_led_on, 8, 3, 60)
    executor.submit(turn_led_on, 7, 3, 70)
    executor.submit(turn_led_on, 1, 3, 80)
    time.sleep(1)
    executor.submit(turn_led_off, 18)
