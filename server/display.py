import time

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


oled_reset = digitalio.DigitalInOut(board.D27)

WIDTH = 128
HEIGHT = 32

i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, reset=oled_reset)
oled.rotation = 2


def clear_display():
    oled.fill(0)
    oled.show()


clear_display()

image = Image.new("1", (oled.width, oled.height))  # mode '1' for 1-bit color
draw = ImageDraw.Draw(image)

font = ImageFont.load_default(size=14)


def display_text(text: str):
    bbox = font.getbbox(text)
    (font_width, font_height) = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )

    oled.image(image)
    oled.show()
