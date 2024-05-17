
import time
import RPi.GPIO as GPIO
from modules import rotary
from modules import constant

GPIO.setmode(GPIO.BOARD)
#GPIO.setmode(GPIO.BCM)
 
swithRelease = 0
rotateDirection = 'none'

def rotaryRotateCall(direction):
  global rotateDirection
  print('Rotate to ' + direction)
  rotateDirection = direction

def rotarySwitchCall(switchStatus):
  global swithRelease
  print('switchStatus')

oRotary = rotary.rotary(
  switch_callback=rotarySwitchCall,
  rotate_callback=rotaryRotateCall
)


while(True):
  time.sleep(0.5)