import RPi.GPIO as GPIO
import time

# Pin definitions
led_pins = [18, 23, 24, 25, 8, 7, 1]

# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Set up each pin as an output
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

try:
    while True:
        for pin in led_pins:
            GPIO.output(pin, GPIO.HIGH)  # Turn on LED
            time.sleep(1)  # Wait 1 second
#            GPIO.output(pin, GPIO.LOW)   # Turn off LED
#           time.sleep(1)               # Wait 1 second

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on CTRL+C exit
