import sys
import os
import re
import signal
import logging
import argparse
import time
import configparser
import pprint
import datetime
import hashlib
import pygame
from elevenlabs import Voice, VoiceSettings, save, play
from elevenlabs.client import ElevenLabs

from modules import core
from modules import constant

# ===========================================================================
# speak Class
# ===========================================================================

class speak():

  def __init__(self):
    self.core = core.core()
    self.verbose = False
    self.logging = False
    self.volume = 0.1
    logging_level: int = self.core.readConf("level", "logging", 20)
    logging.basicConfig(level=int(logging_level))
    
  def say(self, sentence):

    voiceName = self.core.readConf('voice', 'speak', 'Thomas')
    
    client = ElevenLabs(
      api_key = self.core.readConf('api_key', 'speak', '')
    )
    
    hashKey = hashlib.sha1()
    hashKey.update(str(voiceName + sentence).encode('utf-8'))
    fileKey = hashKey.hexdigest()
    
    fileName = self.core.getRootPath() + "cache/" + fileKey + ".mp3"
    
    #response = client.voices.get_all()
    #print(response)
    
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

      self.volume = self.core.readConf('volume', 'speak', 15)

      pygame.mixer.init()
      pygame.mixer.music.load(fileName)
      pygame.mixer.music.set_volume(int(self.volume) / 10)
      pygame.mixer.music.play()

      while pygame.mixer.music.get_busy() == True:
  	    pass
	