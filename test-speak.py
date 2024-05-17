import time
import logging
import os
import pprint
from pathlib import Path
from modules import speak
from modules import constant

scriptName = Path(__file__).stem
logging_level = 20
logging_path =  '.'
logging.basicConfig(filename=logging_path + '/' + scriptName + '.log', level=int(logging_level))

oSpeak = speak.speak()
oSpeak.verbose = True
oSpeak.logging = logging
oSpeak.say("Initialisation en cours...", 10)

#while(True):
#  time.sleep(0.5)