import RPi.GPIO as GPIO
import time
import math
import sys
import threading
from pprint import pprint
from modules import constant
from mfrc522 import MFRC522
from mfrc522 import SimpleMFRC522

class rfid():
  
  def __init__(self, **params):

    GPIO.cleanup()
    self.reader = SimpleMFRC522()
    #self.pollSecond = 0.2
    #self.exitLoop = False
    #self.threadRead = None
    self.lastId = None
    self.lastText = None
    
    self.changeCallback = None
    self.insertCallback = None
    self.removeCallback = None

    if 'remove_callback' in params:
      self.removeCallback = params['remove_callback']

    if 'insert_callback' in params:
      self.insertCallback = params['insert_callback']

    if 'change_callback' in params:
      self.changeCallback = params['change_callback']

  def write(self, text):
    self.reader.write(text)

  def loop(self):
    try:
      timeout = 1
      idx = 0
      id, text = self.reader.read_no_block()
      while not id and idx<timeout:
        id, text = self.reader.read_no_block()
        idx = idx + 0.100
        time.sleep(0.01)

      if self.lastId != id:
          self.triggerChange(str(id), str(text), str(self.lastId), str(self.lastText))

      if self.lastId is None and not id is None:
          self.triggerInsert(str(id), str(text))

      if not self.lastId is None and id is None:
          self.triggerRemove(str(self.lastId), str(self.lastText))

      self.lastId = id
      self.lastText = text

    except:
      print("Unexpected error:", sys.exc_info()[0])
      raise

  def triggerChange(self, id, text, idOld, textOld):
    if not self.changeCallback is None:
      self.changeCallback(id, text, idOld, textOld)

  def triggerInsert(self, id, text):
    if not self.insertCallback is None:
      self.insertCallback(id, text)

  def triggerRemove(self, id, text):
    if not self.removeCallback is None:
      self.removeCallback(id, text)

#  def readLoop(self):    
#    while(True):
#      
#      if self.exitLoop:
#        print("exitLoop")
#        break;
#
#      try:
#        timeout = 1
#        idx = 0
#        id, text = self.reader.read_no_block()
#        while not id and idx<timeout:
#          id, text = self.reader.read_no_block()
#          idx = idx + 0.100
#          time.sleep(0.01)
#
#        if self.lastId != id:
#            self.triggerChange(str(id), str(text), str(self.lastId), str(self.lastText))
#
#        if self.lastId is None and not id is None:
#            self.triggerInsert(str(id), str(text))
#
#        if not self.lastId is None and id is None:
#            self.triggerRemove(str(self.lastId), str(self.lastText))
#
#        self.lastId = id
#        self.lastText = text
#
#        time.sleep(self.pollSecond)
#
#      #except KeyboardInterrupt:
#      #    self.exitLoop=True
#      except:
#        print("Unexpected error:", sys.exc_info()[0])
#        raise

#  def exit(self):
#    self.exitLoop = True
#    GPIO.cleanup()
#subidy:song:8dcfef8ac4abf9d915eace336f4c4ad5