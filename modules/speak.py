import sys
import os
import re
import signal
import logging
import argparse
import time
import configparser
import pprint
import json
import datetime
import hashlib
from elevenlabs import Voice, VoiceSettings, save, play
from elevenlabs.client import ElevenLabs

from modules import core
from modules import constant
from modules import mopidy

# ===========================================================================
# speak Class
# ===========================================================================

class speak():

  def __init__(self, **params):
    self.core = None
    self.mopidy = None
    self.verbose = False
    self.logging = False
    self.volume = 0

    if 'core' in params:
      self.core = params['core']

    if 'mopidy' in params:
      self.mopidy = params['mopidy']

    if 'logging' in params:
      self.logging = params['logging']
    else:
      logging_level: int = self.core.getDebugLevelFromText(self.core.readConf("level", "logging", 'INFO'))
      logging.basicConfig(level=int(logging_level))

  def setVerbose(self, verbose):
    self.verbose = verbose

  def stop(self):
    self.mopidy.stop()
    self.mopidy.tracklist_clear()

  def say(self, sentence, volume = None, repeat = False):

    voiceName = self.core.readConf('voice', 'speak', 'Thomas')
    
    client = ElevenLabs(
      api_key = self.core.readConf('api_key', 'speak', '')
    )

    #response = client.voices.get_all()
    #print(response)
    
    hashKey = hashlib.sha1()
    hashKey.update(str(voiceName + sentence).encode('utf-8'))
    fileKey = hashKey.hexdigest()

    fileNameDetail = self.core.getRootPath() + "speak/" + fileKey + ".json"
    if not os.path.isfile(fileNameDetail):
      if self.verbose:
        print("File " + fileNameDetail + " not already exist for sentence " + sentence + " and voice " + voiceName)

      f = open(fileNameDetail, 'w')
      f.write(json.dumps({
        "sentence": sentence,
        "voice": voiceName,
        "key": fileKey
      }))
      f.close()

    fileName = self.core.getRootPath() + "speak/" + fileKey + ".mp3"    
    if os.path.isfile(fileName):
      if self.verbose:
        print("File " + fileName + " already exist for sentence " + sentence + " and voice " + voiceName)
    
    else:
      if self.verbose:
        print("Generate file " + fileName + " for sentence " + sentence + " and voice " + voiceName)
    
      audio = client.generate(
        text=sentence,
        voice=voiceName,
        voice_settings=VoiceSettings(stability=0.71, similarity_boost=0.4, style=0.0, use_speaker_boost=True),
        model="eleven_multilingual_v1"
      )
    
      save(audio, fileName)
    
      if self.verbose:
        print("Generated.")
    
    if os.path.isfile(fileName):
      if self.verbose:
        print(fileKey + ".mp3")

      if volume==None:
        self.volume = self.core.readConf('volume', 'speak', 15)
        if self.verbose:
          print("Set speak volume " + str(self.volume) + " from conf")
      else:
        self.volume = volume
        if self.verbose:
          print("Set speak volume " + str(self.volume) + " by value")

      sUrl = 'file:///opt/morphee/speak/' + fileKey + '.mp3'

      #self.core.setBeforeMode(self.core.getMode())
      #self.core.setMode(constant.STATE_MODE_SAY)
      #self.mopidy.volume_set(self.volume)
      #self.mopidy.tracklist_repeat(repeat)
      #self.mopidy.new_playlist(sUrl)

