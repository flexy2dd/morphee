from modules import constant
from modules import emails
from modules import core
from pathlib import Path
import time
import argparse
import logging
import os
import pprint

# ===========================================================================
# Param
# ===========================================================================
parser = argparse.ArgumentParser(description="Morphe manager service")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
parser.add_argument("-V", "--volume", help="volume (0 > 100)", type=int, default=10)
parser.add_argument("-b", "--body", help="body", type=str, default="Body")
parser.add_argument("-s", "--subject", help="subject", type=str, default="Subject...")
parser.add_argument("-t", "--to", help="to", type=str, default="flexy2dd@gmail.com")
args = parser.parse_args()

scriptName = Path(__file__).stem
logging_level = 20
logging_path =  '.'
logging.basicConfig(filename=logging_path + '/' + scriptName + '.log', level=int(logging_level))

scriptName = Path(__file__).stem
oCore = core.core(scriptName)
oCore.verbose = True

oEmails = emails.emails(
  core = oCore,
  logging = logging
)
oEmails.verbose = True
oEmails.send(args.body, args.subject, args.to)