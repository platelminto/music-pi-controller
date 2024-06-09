import socket
import json
import os
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import requests

MAIN_LEDS = [18, 23, 24, 25, 8, 7, 1]

DEBUG = True

API_URL = "http://127.0.0.1:5000/"  # URL to your Flask server


class Controller:
    def __init__(self, pi_ip=None, pi_port=None, debug=False):
        self.pi_ip = pi_ip
        self.pi_port = pi_port
        self.debug = debug

    def send_command(self, command):
        if self.debug:
            try:
                requests.post(API_URL + command["cmd"], json=command)
            except requests.exceptions.ConnectionError:
                pass
        # UDP socket communication
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = json.dumps(command)
        sock.sendto(message.encode(), (self.pi_ip, self.pi_port))
        sock.close()

    def show_text(self, text: str, duration: Optional[float] = None):
        command = {"cmd": "display-print", "message": text}
        self.send_command(command)

        if duration:
            time.sleep(duration)
            self.clear_text()

    def clear_text(self):
        command = {"cmd": "display-clear"}
        self.send_command(command)

    def turn_led_on(self, led_id: int, duration: Optional[float] = None, power_percentage: int = 100):
        if not (0 <= power_percentage <= 100):
            raise ValueError("Power percentage must be between 0 and 100")

        command = {"cmd": "set-led", "pin": led_id, "power": power_percentage}  # Adjust command structure for HTTP API

        self.send_command(command)

        if duration:
            time.sleep(duration)
            self.turn_led_off(led_id)

    def turn_led_off(self, led_id):
        self.turn_led_on(led_id, power_percentage=0)

    def cleanup(self):
        for led in MAIN_LEDS:
            self.turn_led_off(led)

        self.clear_text()


if __name__ == "__main__":
    controller = Controller(debug=DEBUG)

    # controller.turn_led_on(18, 3, 100)

    executor = ThreadPoolExecutor()
    executor.submit(controller.turn_led_on, 18, None, 20)
    executor.submit(controller.turn_led_on, 23, 3, 30)
    executor.submit(controller.turn_led_on, 24, 3, 40)
    executor.submit(controller.turn_led_on, 25, 3, 50)
    executor.submit(controller.turn_led_on, 8, 3, 60)
    executor.submit(controller.turn_led_on, 7, 3, 70)
    executor.submit(controller.turn_led_on, 1, 3, 80)
    time.sleep(1)
    executor.submit(controller.turn_led_off, 18)

