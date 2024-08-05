import argparse
import time
import logging
import os
import pprint
from pathlib import Path
from modules import speak
from modules import constant
from modules import core

# ===========================================================================
# Param
# ===========================================================================
parser = argparse.ArgumentParser(description="Morphe manager service")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
parser.add_argument("-V", "--volume", help="volume (0 > 100)", type=int, default=10)
parser.add_argument("-s", "--sentence", help="sentence", type=str, default="Initialisation en cours...")
args = parser.parse_args()

scriptName = Path(__file__).stem
logging_level = 20
logging_path =  '.'
logging.basicConfig(filename=logging_path + '/' + scriptName + '.log', level=int(logging_level))

scriptName = Path(__file__).stem
oCore = core.core(scriptName)
oCore.verbose = True

oSpeak = speak.speak(
  core = oCore,
  logging = logging
)
oSpeak.verbose = True
oSpeak.say(args.sentence, args.volume)

#while(True):
#  time.sleep(0.5)