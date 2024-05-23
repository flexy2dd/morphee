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

oScreen.wait(True, 'Mon titre le plus long')

oScreen.println('Ligne 1')
oScreen.println('Mon titre le plus long')
  
time.sleep(5)

#while(True):
#  oScreen.wait(True)
#  time.sleep(0.5)
