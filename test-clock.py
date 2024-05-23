import time
import logging
import os
import pprint
from pathlib import Path
from modules import screen
from modules import constant

scriptName = Path(__file__).stem
logging_level = 20
logging_path =  '.'
logging.basicConfig(filename=logging_path + '/' + scriptName + '.log', level=int(logging_level))

oScreen = screen.screen()
oScreen.verbose = True
oScreen.logging = logging

while(True):
  oScreen.clock()
  time.sleep(0.001)

#while(True):
#  time.sleep(0.5)