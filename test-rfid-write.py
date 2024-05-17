#!/usr/bin/env python
import json
import time
from modules import constant
from modules import tools
from modules import rfid
from modules import screen
import RPi.GPIO as GPIO
#from mfrc522 import SimpleMFRC522
from modules.mfrc522.MFRC522 import MFRC522

oScreen = screen.screen()
oScreen.cls()

oRfid = rfid.rfid(
)

oRfid.waitInsert(30, oScreen)

textEncode = json.dumps({
  "style": "music",
  "url": "subidy:song:9cd37c1d26daf0778bc995704c9aebfa",
  "mode": "once"
}, separators=(',', ':'))
print('Try encode with ' + textEncode)

oScreen.picto("cogs")
id, text = oRfid.writeSectors(textEncode, [constant.SECTOR_1, constant.SECTOR_2, constant.SECTOR_3, constant.SECTOR_4, constant.SECTOR_5])
print("write text: " + text)
time.sleep(4)

oRfid.waitRemove(30, oScreen)

id, text = oRfid.readSectors([constant.SECTOR_1, constant.SECTOR_2, constant.SECTOR_3, constant.SECTOR_4, constant.SECTOR_5])
print("read text: " + text)

#encoded = False
#
#id, text_in = oRfid.reader.write_no_block(textEncode)
#
#loopTimeout = constant.CARD_ENCODE_TIMEOUT
#loopStartTime = time.time()
#loopTimeoutTime = time.time() + loopTimeout
#while time.time() <= loopTimeoutTime:
#  loopStep = int(loopTimeoutTime-time.time())
#
#  if id:
#    encoded = True
#    print("Is encoded")
#    break
#
#  id, text_in = oRfid.reader.write_no_block(textEncode)    
