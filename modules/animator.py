import math
import time
import threading
import RPi.GPIO as GPIO
import board
import neopixel

from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.color import RED, WHITE

class animator():
  
  def __init__(self, **params):

    #GPIO.cleanup()
    self.pollSecond = 0.2
    self.exitLoop = False

    self.pixels = neopixel.NeoPixel(board.D12, 24, brightness=0.5, auto_write=False, pixel_order="GRB")
    self.sparkle = Sparkle(self.pixels, speed=0.5, color=WHITE, num_sparkles=5)
    self.comet = Comet(self.pixels, speed=0.5, color=WHITE, tail_length=4, bounce=True)
    self.chase = Chase(self.pixels, speed=0.5, color=WHITE, size=3, spacing=6)

  def run(self):
    self.threadRead = threading.Thread(target=self.animLoop, daemon=True)
    self.threadRead.start()
    #self.threadRead.join()

  def animLoop(self):    
    while(True):
      
      if self.exitLoop:
        print("exitLoop")
        break;

      try:
        self.comet.animate()
        #time.sleep(self.pollSecond)
      #except KeyboardInterrupt:
      #    self.exitLoop=True
      except:
        print("Unexpected error:", sys.exc_info()[0])
        raise