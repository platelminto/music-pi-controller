import socket
import json
import os
import time
from time import sleep

from dotenv import load_dotenv

load_dotenv()

pi_ip = os.getenv("PI_IP")
pi_port = int(os.getenv("PI_PORT"))


def send_command(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    message = json.dumps(command)
    print(pi_ip, pi_port, message)
    sock.sendto(message.encode(), (pi_ip, pi_port))


def register_leds(led_pins):
    command = {"cmd": "register-leds", "pins": led_pins}

    send_command(command)


def turn_led_on(led_id):
    command = {"cmd": "led-on", "pin": led_id}

    send_command(command)


def turn_led_off(led_id):
    command = {"cmd": "led-off", "pin": led_id}

    send_command(command)


def set_led_power(led_id, power_percentage):
    if not (0 <= power_percentage <= 100):
        raise ValueError("Power percentage must be between 0 and 100")

    # command = {"cmd": "set-power", "pin": led_id, "power": power_percentage}
    command = {"cmd": "set-power", "pin": led_id}

    send_command(command)


def debug_print(message):
    command = {"cmd": "debug-print", "message": message}

    send_command(command)


if __name__ == "__main__":
    led_ids = [18, 23, 24, 25, 8, 7, 1]
    power_percentage = 50  # Set LED to 50% power
    # set_led_power(led_id, power_percentage)

    register_leds(led_ids)

    # for led_id in led_ids:
    #     turn_led_on(led_id)
    #     time.sleep(0.6)
    #     turn_led_off(led_id)
