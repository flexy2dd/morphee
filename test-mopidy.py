#!/usr/bin/env python
import json
import time
import pprint
from modules import constant
from modules import tools
from modules import screen
from modules import mopidy
from modules import core
from pathlib import Path
import RPi.GPIO as GPIO

scriptName = Path(__file__).stem
oCore = core.core(scriptName)
print(oCore.scriptName)
print(oCore.mqttClientId)

def mopidyStatusChange(status, oldStatus):
  print('change ' + oldStatus + ' to ' + status)
  
oMopidy = mopidy.mopidy(
  core = oCore,
  change_callback=mopidyStatusChange
)
oMopidy.verbose = True

while True:
  time.sleep(0.1)
#(self, uri, isOnce = True, isShuffle = False, isLoop = False):
  
#oMopidy.create_playlist(
#  'subidy:album:59d8f838a9414b3a33f52b11f8634c46',
#  True,
#  True,
#  False
#)




#oScreen = screen.screen()
#oScreen.cls()
#
#result = {
#  'mode': 'once', 
#  'style': 'music', 
#  'url': '', 
#  'length': 155000, 
#  'position': 91555, 
#  'artist': 'Salebarbes', 
#  'album': 'À boire deboutte', 
#  'name': "Y a l'bon Dieu qui l'attend",
#  'id': '',
#  'volume': 75
#}
#oScreen.play(result)
#while(True):
#  time.sleep(0.001)

#
#resultOld = {
#  'length': 10,
#}
#
#oMopidy = mopidy.mopidy()
#result = oMopidy.get_playing_details()
#
#result = {**resultOld, **result}
#
#print(type(result))
#pprint.pprint(result)

