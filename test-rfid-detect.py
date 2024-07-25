
import RPi.GPIO as GPIO
from modules import constant
import board
import time


GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(10)

def cardPresenceCall(channel):
  state = GPIO.input(constant.GPIO_RFID_DETECT)
  if state == 0:
    print('remove')
  else: 
    print('insert')

GPIO.setup(constant.GPIO_RFID_DETECT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.add_event_detect(constant.GPIO_RFID_DETECT, GPIO.BOTH, callback=cardPresenceCall, bouncetime=50) 

try:
    while True:
      time.sleep(1)
      state = GPIO.input(constant.GPIO_RFID_DETECT)
      print(state)
except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on program exit

