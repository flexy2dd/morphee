import time
import board
import neopixel
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.color import PINK


pixels = neopixel.NeoPixel(board.D12, 24, brightness=0.5, auto_write=False, pixel_order="GRB")
pixels.fill((0, 0, 0))
pixels.show()