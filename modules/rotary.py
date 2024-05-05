import RPi.GPIO as GPIO
import time
import math
from pprint import pprint
from modules import constant

# Inspired by https://github.com/petervflocke/rotaryencoder_rpi
class rotary():
  
  def __init__(self, **params):
    
    self.SWPrev = 1
    self.last_delta = 0
    self.r_seq = 0
    self.steps_per_cycle = 4
    self.remainder = 0
    self.cycles = 0
    self.delta = 0

    self.trigger = True

    self.pinCLK = constant.GPIO_ROTARY_CLK
    self.pinDT = constant.GPIO_ROTARY_DT
    self.pinSW = constant.GPIO_ROTARY_SW

    #GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Rotation
    GPIO.setup(self.pinCLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(self.pinCLK, GPIO.BOTH, callback=self.rotaryCall)
    
    GPIO.setup(self.pinDT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(self.pinDT, GPIO.BOTH, callback=self.rotaryCall)
    
    # Switch
    GPIO.setup(self.pinSW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(self.pinSW, GPIO.BOTH, callback=self.rotarySwitchCall, bouncetime=50) 

    self.lastState = GPIO.input(self.pinCLK)
    
    self.switchCallback = None
    self.rotateCallback = None

    if 'switch_callback' in params:
      self.switchCallback = params['switch_callback']

    if 'rotate_callback' in params:
      self.rotateCallback = params['rotate_callback']

  def triggerDisable(self):
    self.trigger = False

  def triggerEnable(self):
    self.trigger = True

  def triggerRotateClockwise(self):
    if not self.rotateCallback is None and self.trigger:
      pprint('rotate Clockwise')
      self.triggerRotate('left')

  def triggerRotate(self, status):
    if not self.rotateCallback is None and self.trigger:
      self.rotateCallback(status)

  def triggerSwitch(self, status):
    if not self.switchCallback is None and self.trigger:
      self.switchCallback(status)

  def rotaryCall(self, channel):
    delta = 0
    a_state = GPIO.input(self.pinCLK)
    b_state = GPIO.input(self.pinDT)
    r_seq = (a_state ^ b_state) | b_state << 1
    if r_seq != self.r_seq:
        delta = (r_seq - self.r_seq) % 4
        if delta==3:
            delta = -1
        elif delta==2:
            delta = int(math.copysign(delta, self.last_delta))
        self.last_delta = delta
        self.r_seq = r_seq
    self.delta += delta
    self.remainder += delta 
    self.cycles = self.remainder // self.steps_per_cycle
    self.remainder %= self.steps_per_cycle

    # Check rotary status
    if self.cycles == 1:
        self.triggerRotate('left')
        self.delta = 0
    elif self.cycles == -1:
        self.triggerRotate('right')
        self.delta = 0
    else:
        pass

  def rotarySwitchCall(self, channel):
    state = GPIO.input(self.pinSW)
    if state == 0:
        if self.SWPrev == 1:
          self.SWPrev = 0
          self.triggerSwitch('press')
        else:
          pass
    else: 
        if self.SWPrev == 0:
          self.SWPrev = 1
          self.triggerSwitch('release')
        else:
          pass

  def setSwitchCallback(self, switch_callback):
    self.switchCallback = switch_callback

  def setRotateCallback(self, rotate_callback):
    self.rotateCallback = rotate_callback
