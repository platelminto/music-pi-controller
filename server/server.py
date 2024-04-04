import os
import socket
import json
import RPi.GPIO as GPIO
import dotenv

dotenv.load_dotenv()

pi_port = int(os.getenv("PI_PORT"))


GPIO.setmode(GPIO.BCM)


def execute_command(command):
    action = command['action']
    pin = command['pin']
    GPIO.setup(pin, GPIO.OUT)

    if action == 'led-on':
        GPIO.output(pin, GPIO.HIGH)
    elif action == 'led-off':
        GPIO.output(pin, GPIO.LOW)
    elif action == 'set-power':
        power = command['power']
        GPIO.output(pin, GPIO.HIGH)

        # if not (0 <= power <= 100):
        #     raise ValueError("Power percentage must be between 0 and 100")
        # pwm = GPIO.PWM(pin, 100)
        # pwm.start(power)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('', pi_port)
sock.bind(server_address)

while True:
    data, _ = sock.recvfrom(4096)
    command = json.loads(data.decode())  # Deserialize the JSON string to a Python dict
    execute_command(command)
