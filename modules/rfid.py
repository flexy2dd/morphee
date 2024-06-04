import RPi.GPIO as GPIO
import time
import datetime
import math
import sys
import threading
import json
from pprint import pprint
from modules import constant
from modules.mfrc522.MFRC522 import MFRC522
from modules.mfrc522.SimpleMFRC522 import SimpleMFRC522
from modules.mfrc522.BasicMFRC522 import BasicMFRC522

class rfid():
  
  def __init__(self, **params):

    GPIO.cleanup()
    GPIO.setwarnings(False)

    self.reader = BasicMFRC522()
    self.lastId = None
    self.lastJsonDatas = None
    self.loopTimeSecond = 99
    self.cardPresence = 0
    self.changeCallback = None
    self.insertCallback = None
    self.removeCallback = None
    self.presenceCallback = None    
    self.sectors = []
    self.verbose = False
    self.trigger = True

    # Presence card
    GPIO.setup(constant.GPIO_RFID_DETECT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(constant.GPIO_RFID_DETECT, GPIO.BOTH, callback=self.cardPresenceCall, bouncetime=50) 

    if 'remove_callback' in params:
      self.removeCallback = params['remove_callback']

    if 'insert_callback' in params:
      self.insertCallback = params['insert_callback']

    if 'change_callback' in params:
      self.changeCallback = params['change_callback']

    if 'presence_callback' in params:
      self.presenceCallback = params['presence_callback']
      
    if 'sectors' in params:
      self.sectors = params['sectors']

  def cardPresenceCall(self, channel):
    state = GPIO.input(constant.GPIO_RFID_DETECT)
    if state == 0:
        if self.cardPresence == 1:
          self.cardPresence = 0
          if not self.presenceCallback is None:
            self.presenceCallback('remove')
          self.triggerCardRemoved()
        else:
          pass
    else: 
        if self.cardPresence == 0:
          self.cardPresence = 1
          if not self.presenceCallback is None:
            self.presenceCallback('insert')
          self.triggerCardInserted()
        else:
          pass

  def triggerCardRemoved(self):
    if self.verbose:
      print('triggerCardRemoved')

    if self.trigger:
      self.triggerRemove(str(self.lastId), self.lastJsonDatas)

  def triggerCardInserted(self):
    if self.verbose:
      print('triggerCardInserted')

    try:
      id, text = self.readSectors(self.sectors)

      jsonDatas = json.loads(text.strip('\x00'))

      if self.trigger:
        self.triggerInsert(str(id), jsonDatas)

      if self.lastId != id and self.trigger:
        self.triggerChange(str(id), jsonDatas, str(self.lastId), self.lastJsonDatas)
    
      self.lastId = id
      self.lastJsonDatas = jsonDatas
    
    except:
      print("Unexpected error:", sys.exc_info()[0])
      pass
    
  def isInserted(self):
    state = GPIO.input(constant.GPIO_RFID_DETECT)
    if state == 0:
      return False
    else:
      return True

  def setSectors(self, sectors):
    self.sectors = sectors

  def setTrigger(self, trigger):
    self.trigger = trigger

  def setTriggerOff(self):
    self.setTrigger(False)

  def setTriggerOn(self):
    self.setTrigger(True)

  def write(self, text):
    self.reader.write(text)

  def triggerChange(self, id, jsonDatas, idOld, jsonDatasOld):
    if not self.changeCallback is None:
      pprint('call changeCallback')
      self.changeCallback(id, jsonDatas, idOld, jsonDatasOld)

  def triggerInsert(self, id, jsonDatas):
    if not self.insertCallback is None:
      self.insertCallback(id, jsonDatas)

  def triggerRemove(self, id, jsonDatas):
    if not self.removeCallback is None:
      self.removeCallback(id, jsonDatas)

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

#  def loop(self):
#    now = datetime.datetime.now()
#
#    #if now.second != self.loopTimeSecond and now.second in [0, 2, 4, 6, 8, 10, 12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,58]:
#    if now.second != self.loopTimeSecond and now.second in [0,4,8,12,16,20,24,28,32,36,40,44,48,52,58]:
#      self.loopTimeSecond = now.second
#      print('check RFID')
#      try:
#        timeout = 0.5
#        idx = 0
#        id, text = self.reader.read_no_block(constant.SECTOR_1)
#        while not id and idx<timeout:
#          id, text = self.reader.read_no_block(constant.SECTOR_1)
#          idx = idx + 0.1
#          time.sleep(0.1)
#
#        print('OK')
#        if self.lastId != id:
#            self.triggerChange(str(id), str(text), str(self.lastId), str(self.lastJson))
#      
#        if self.lastId is None and not id is None:
#            id, text = self.readSectors([constant.SECTOR_1, constant.SECTOR_2, constant.SECTOR_3, constant.SECTOR_4, constant.SECTOR_5])
#            self.triggerInsert(str(id), str(text))
#      
#        if not self.lastId is None and id is None:
#            self.triggerRemove(str(self.lastId), str(self.lastJson))
#      
#        self.lastId = id
#        self.lastJson = text
#      
#      except:
#        print("Unexpected error:", sys.exc_info()[0])
#        pass

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
    time.sleep(0.1)

    # Retry writing if it fails initially
    while not id:
      id, text_in = self.reader.write_no_block(text, trailer_block)
      time.sleep(0.1)

    # Return the tag ID and the written data
    return id, text_in

  def writeSectors(self, text, trailer_blocks):
    # Split the input text into chunks of 48 characters
    text_formated_list = self.reader._split_string(text)

    if len(text_formated_list)<len(trailer_blocks):
      for i in range(0, len(trailer_blocks)-len(text_formated_list)):
        text_formated_list.append('\0'*48)

    # Initialize an empty string to store the concatenated data
    text_all = ''

      # Iterate through the trailer_blocks list
    for i in range(0, len(trailer_blocks)):
      try:
        # Write data to the sector using the write_sector function
        id, text = self.writeSector(text_formated_list[i], trailer_blocks[i])
        time.sleep(0.1)
        # Concatenate the written data to the text_all string
        text_all += text
      except IndexError:
        # Ignore any index errors that may occur if there are fewer chunks than trailer blocks
        pass

    # Return the tag ID and the concatenated data
    return id, text_all

#subidy:song:8dcfef8ac4abf9d915eace336f4c4ad5

