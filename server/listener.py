import os
import socket
import json
import time

import RPi.GPIO as GPIO
import dotenv

dotenv.load_dotenv()

pi_port = int(os.getenv("PI_PORT"))

pwm_leds = {}


def execute_command(command):
    GPIO.setmode(GPIO.BCM)

    cmd = command['cmd']
    print(command)

    if cmd == 'set-led':
        pin = command['pin']
        power = command['power']

        if not (0 <= power <= 100):
            raise ValueError("Power percentage must be between 0 and 100")

        if pin not in pwm_leds:
            GPIO.setup(pin, GPIO.OUT)
            pwm_leds[pin] = GPIO.PWM(pin, 200)
            pwm_leds[pin].start(0)

        pwm = pwm_leds[pin]
        duty_cycle = power
        pwm.ChangeDutyCycle(duty_cycle)
    elif cmd == 'debug-print':
        message = command['message']

        print(message)
    else:
        print(f"Unknown command: {cmd}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('', pi_port)
sock.bind(server_address)
print(f'Listening on port {pi_port}...')

try:
    while True:
        data, _ = sock.recvfrom(4096)
        command = json.loads(data.decode())  # Deserialize the JSON string to a Python dict
        execute_command(command)
except KeyboardInterrupt:
    pass
finally:
    for pwm in pwm_leds.values():
        pwm.stop()
    GPIO.cleanup()
