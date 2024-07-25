import re
import os
import time
import hashlib
import string
import pprint
import RPi.GPIO as GPIO
import glob
import configparser
import random
from datetime import datetime
from pathlib import Path
from modules import constant
from os import listdir
from os.path import isfile, join

# ===========================================================================
# core Class
# ===========================================================================

class core():

  def __init__(self, scriptName):
    self.scriptName = scriptName
    self.confFile = constant.CORE_CONF
    self.verbose = False
    self.beforeMode = None
    self.mode = constant.STATE_MODE_STARTING
    self.modeUpdated = datetime.now()
    self.mqttClientId = f"mqtt-{self.scriptName}-{random.randint(0, 1000)}"
    
  def debug(self, message):
    if self.verbose:
      print(message)

  def getDebugLevelFromText(self, level):
      return int(constant.DEBUG_LEVELS[level])

  def getModeDelta(self):
    now = datetime.now()
    
    delta = now - self.modeUpdated

    return delta.total_seconds()

  def setMode(self, mode):
    if self.verbose:
      print('set mode to ' + mode)

    self.modeUpdated = datetime.now()

    self.mode = mode

  def getMode(self):
    return self.mode

  def setBeforeMode(self, beforeMode):
    if self.verbose:
      print('set before mode to ' + beforeMode)

    self.beforeMode = beforeMode

  def getBeforeMode(self):
    return self.beforeMode

  def clearBeforeMode(self):
    self.beforeMode = None

  def getFilePid(self):
    return '%s/../%s' % (os.path.dirname(__file__), constant.CORE_PID)

  def getFileConf(self):
    return '%s/../%s' % (os.path.dirname(__file__), constant.CORE_CONF)

  def getRootPath(self):
    return '%s/../' % (os.path.dirname(__file__))

  def getConf(self):
    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)
  
      if oConf.has_option('general', 'title'):
        generalTitle = oConf.get('general', 'title')
  
      return oConf
  
    return False

  def readConf(self, sKey, sSection = 'general', mDefault = False):
    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)
  
      if oConf.has_option(sSection, sKey):
        return oConf.get(sSection, sKey)
  
    return mDefault

  def readGeneralConf(self, sKey, mDefault = False):
    return readConf(sKey, 'general', mDefault)

  def isRunning(self):
    return false
    
  def encodeCard(self, url):
    return false

  def setLight(self, light):
    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)

      if int(light) in [constant.LIGHT_ON, constant.LIGHT_OFF]:
        oConf.set('general', 'light', str(light))

        with open(self.confFile, 'w') as configfile:
          oConf.write(configfile)

        return True

    return False;

  def getLight(self):
    oConf = self.getConf()
    return int(oConf.get('general', 'light', fallback=constant.LIGHT_ON))

  def getVolumeStep(self):
    oConf = self.getConf()
    return int(oConf.get('general', 'volume_step', fallback='4'))

  def setGeneralVolume(self, volume):
    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)

      if volume < 0:
        volume = 0
      elif volume > 100:
        volume = 100

      oConf.set('general', 'volume', str(volume))
    
      with open(self.confFile, 'w') as configfile:
        oConf.write(configfile)

      return True

    return False;

  def getGeneralVolume(self):
    oConf = self.getConf()
    return int(oConf.get('general', 'volume', fallback='10'))

  def setSpecificVolume(self, idTrack, volume):
    
    if volume < 0:
      volume = 0
    elif volume > 100:
      volume = 100

    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)

      if not oConf.has_section('track-' + idTrack):
        oConf.add_section('track-' + idTrack)

      oConf.set('track-' + idTrack, 'volume', str(volume))
    
      with open(self.confFile, 'w') as configfile:
        oConf.write(configfile)

      return True

    return False;

  def getSpecificVolume(self, idTrack):
    oConf = self.getConf()
    defaultVolume = self.getGeneralVolume()
    return int(oConf.get('track-' + idTrack, 'volume', fallback=defaultVolume))

  def setSpeakVolume(self, volume):
    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)

      oConf.set('speak', 'volume', str(volume))
    
      with open(self.confFile, 'w') as configfile:
        oConf.write(configfile)

      return True

    return False;

  def getSpeakVolume(self):
    oConf = self.getConf()
    return int(oConf.get('speak', 'volume', fallback='30'))

  def setAnimBrightness(self, brightness):
    if brightness>255:
      brightness = 255

    if brightness<0:
      brightness = 0

    if os.path.isfile(self.brightness):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)

      oConf.set('animation', 'brightness', str(brightness))
    
      with open(self.confFile, 'w') as configfile:
        oConf.write(configfile)

      return True

    return False;

  def getAnimBrightness(self):
    oConf = self.getConf()
    return int(oConf.get('animation', 'brightness', fallback='50'))

  def setScreenContrast(self, contrast):

    if contrast>255:
      contrast = 255

    if contrast<0:
      contrast = 0

    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)

      oConf.set('screen', 'contrast', str(contrast))
    
      with open(self.confFile, 'w') as configfile:
        oConf.write(configfile)

      return True

    return False;

  def getScreenContrast(self):
    oConf = self.getConf()
    return int(oConf.get('screen', 'contrast', fallback='50'))
