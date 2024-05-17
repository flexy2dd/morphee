# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.color import RED, WHITE


pixels = neopixel.NeoPixel(board.D12, 24, brightness=0.5, auto_write=False, pixel_order="GRB")

sparkle = Sparkle(pixels, speed=0.5, color=WHITE, num_sparkles=5)
comet = Comet(pixels, speed=0.05, color=WHITE, tail_length=4, bounce=True)
chase = Chase(pixels, speed=0.05, color=WHITE, size=3, spacing=6)

while True:
  #comet.animate();
  chase.animate();

