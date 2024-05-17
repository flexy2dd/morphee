import RPi.GPIO as GPIO
import time
import math
import sys
import threading
from pprint import pprint
from modules import constant
from modules.mfrc522.MFRC522 import MFRC522
from modules.mfrc522.SimpleMFRC522 import SimpleMFRC522
from modules.mfrc522.BasicMFRC522 import BasicMFRC522

class rfid():
  
  def __init__(self, **params):

    GPIO.cleanup()
    self.reader = BasicMFRC522()
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
      id, text = self.reader.read_no_block(constant.SECTOR_1)
      while not id and idx<timeout:
        id, text = self.reader.read_no_block(constant.SECTOR_1)
        idx = idx + 0.100
        time.sleep(0.01)

      if self.lastId != id:
          self.triggerChange(str(id), str(text), str(self.lastId), str(self.lastText))

      if self.lastId is None and not id is None:
          id, text = self.readSectors([constant.SECTOR_1, constant.SECTOR_2, constant.SECTOR_3, constant.SECTOR_4, constant.SECTOR_5])
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

  def waitInsert(self, loopTimeout = 30, oScreen = None):
    id, text = self.reader.read_no_block(constant.SECTOR_1)
    loopStartTime = time.time()
    loopTimeoutTime = time.time() + loopTimeout
    while time.time() <= loopTimeoutTime:
      loopStep = int(loopTimeoutTime-time.time())
      
      if oScreen != None:
        oScreen.countdown(loopStep + 1, 'arrow-down', 'Veuillez inserer une carte')

      if id:
        if oScreen != None:
          oScreen.cls()
        return True

      id, text = self.reader.read_no_block(constant.SECTOR_1)

    if oScreen != None:
      oScreen.cls()

    return False

  def waitRemove(self, loopTimeout = 60, oScreen = None):
    id = 123456789
    loopStartTime = time.time()
    loopTimeoutTime = time.time() + loopTimeout
    while time.time() <= loopTimeoutTime:
      loopStep = int(loopTimeoutTime-time.time())
      
      if oScreen != None:
        oScreen.countdown(loopStep + 1, 'arrow-up', 'Veuillez retirer la carte')

      timeout = 1
      idx = 0
      id, text = self.reader.read_no_block(constant.SECTOR_1)
      while not id and idx<timeout:
        id, text = self.reader.read_no_block(constant.SECTOR_1)
        idx = idx + 0.100
        time.sleep(0.01)

      if id == None:
        if oScreen != None:
          oScreen.cls()
        return True

    if oScreen != None:
      oScreen.cls()

    return False

  def readSector(self, trailer_block):
    id, text = self.reader.read_no_block(trailer_block)
    while not id:
      id, text = self.reader.read_no_block(trailer_block)
    return id, text

  def readSectors(self, trailer_blocks):
    text_all = ''
    for trailer_block in trailer_blocks:
      id, text = self.readSector(trailer_block)
      text_all += text
    return id, text_all

  def writeSector(self, text, trailer_block):
    # Write the data to the RFID tag using the helper function write_no_block
    id, text_in = self.reader.write_no_block(text, trailer_block)

    # Retry writing if it fails initially
    while not id:
      id, text_in = self.reader.write_no_block(text, trailer_block)

    # Return the tag ID and the written data
    return id, text_in

  def writeSectors(self, text, trailer_blocks):
    # Split the input text into chunks of 48 characters
    text_formated_list = self.reader._split_string(text)

    # Initialize an empty string to store the concatenated data
    text_all = ''

      # Iterate through the trailer_blocks list
    for i in range(0, len(trailer_blocks)):
      try:
        # Write data to the sector using the write_sector function
        id, text = self.writeSector(text_formated_list[i], trailer_blocks[i])

        # Concatenate the written data to the text_all string
        text_all += text
      except IndexError:
        # Ignore any index errors that may occur if there are fewer chunks than trailer blocks
        pass

    # Return the tag ID and the concatenated data
    return id, text_all

#subidy:song:8dcfef8ac4abf9d915eace336f4c4ad5