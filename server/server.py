import os
import socket
import json
import time

import RPi.GPIO as GPIO
import dotenv

dotenv.load_dotenv()

pi_port = int(os.getenv("PI_PORT"))

GPIO.setmode(GPIO.BCM)


def execute_command(command):
    cmd = command['cmd']

    if cmd == 'register-leds':
        pins = command['pins']

        for pin in pins:
            print(f"Registering LED {pin}")
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    elif cmd == 'led-on':
        pin = command['pin']
        print(f"Turning on LED {pin}")
        GPIO.output(pin, GPIO.HIGH)
    elif cmd == 'led-off':
        pin = command['pin']
        print(f"Turning off LED {pin}")
        GPIO.output(pin, GPIO.LOW)
    elif cmd == 'set-power':
        pin = command['pin']
        power = command['power']

        GPIO.output(pin, GPIO.HIGH)

        # if not (0 <= power <= 100):
        #     raise ValueError("Power percentage must be between 0 and 100")
        # pwm = GPIO.PWM(pin, 100)
        # pwm.start(power)
    elif cmd == 'debug-print':
        message = command['message']

        print(message)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('', pi_port)
sock.bind(server_address)
print(f'Listening on port {pi_port}...')

while True:
    data, _ = sock.recvfrom(4096)
    command = json.loads(data.decode())  # Deserialize the JSON string to a Python dict
    execute_command(command)
