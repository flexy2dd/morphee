#!/usr/bin/env python
import json
import time
import pprint
from modules import constant
from modules import tools
from modules import screen
from modules import mopidy
import RPi.GPIO as GPIO

oScreen = screen.screen()
oScreen.cls()

result = {
  'mode': 'once', 
  'style': 'music', 
  'url': '', 
  'length': 155000, 
  'position': 91555, 
  'artist': 'Salebarbes', 
  'album': 'À boire deboutte', 
  'name': "Y a l'bon Dieu qui l'attend",
  'id': '',
  'volume': 75
}
oScreen.play(result)
while(True):
  time.sleep(0.001)

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

