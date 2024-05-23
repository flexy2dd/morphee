import re
import os
import time
import hashlib
import string
import datetime
import pprint
import RPi.GPIO as GPIO
import glob
import configparser
import random
from modules import constant
from os import listdir
from os.path import isfile, join

# ===========================================================================
# core Class
# ===========================================================================

class core():

  def __init__(self):
    self.confFile = constant.CORE_CONF
    self.verbose = False
    
  def debug(self, message):
    if self.verbose:
      print(message)

  def getDebugLevelFromText(self, level):
      return int(constant.DEBUG_LEVELS[level])

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

#  def getRemainingSeconds(self):
#    nowTime = time.mktime(datetime.datetime.now().replace(microsecond=0).timetuple())
#    targetTime = nowTime
#
#    if os.path.isfile(constant.CORE_PID):
#      f = open(constant.CORE_PID, "r")
#      targetTime = f.read()
#
#    targetTime = datetime.datetime.fromtimestamp(float(targetTime)) 
#    nowTime = datetime.datetime.fromtimestamp(float(nowTime))
#    
#    if targetTime < nowTime:
#      return 0
#
#    timeDelta = targetTime - nowTime
#
#    return timeDelta.total_seconds()
#
#  def getRemainingTime(self, bIncludeSeconds = False):
#    seconds = self.getRemainingSeconds()
#
#    hours = seconds // (60*60)
#    seconds %= (60*60)
#    minutes = seconds // 60
#    seconds %= 60
#
#    if bIncludeSeconds:
#      return "%02i:%02i:%02i" % (hours, minutes, seconds)
#      
#    return "%02i:%02i" % (hours, minutes)
#
#  def setRain(self, rain):
#    if os.path.isfile(self.confFile):
#      ambiance = configparser.ConfigParser()
#      ambiance.read(self.confFile)
#
#      if int(rain) in [constant.RAIN_LEVEL_NONE, constant.RAIN_LEVEL_LIGHT, constant.RAIN_LEVEL_MODERATE, constant.RAIN_LEVEL_HEAVY]:
#        ambiance.set('general', 'rain', str(rain))
#
#        with open(self.confFile, 'w') as configfile:
#          ambiance.write(configfile)
#
#        return True
#
#    return False;
#
#  def getRain(self):
#    ambiance = self.getConf()
#    return int(ambiance.get('general', 'rain', fallback=constant.RAIN_LEVEL_NONE))
#
#  def setThunder(self, thunderstorm):
#    if os.path.isfile(self.confFile):
#      ambiance = configparser.ConfigParser()
#      ambiance.read(self.confFile)
#
#      if int(thunderstorm) in [constant.THUNDERSTORM_LEVEL_NONE, constant.THUNDERSTORM_LEVEL_LIGHT, constant.THUNDERSTORM_LEVEL_MODERATE, constant.THUNDERSTORM_LEVEL_HEAVY]:
#        ambiance.set('general', 'thunder', str(thunderstorm))
#
#        with open(self.confFile, 'w') as configfile:
#          ambiance.write(configfile)
#
#        return True
#
#    return False;
#
#  def getThunder(self):
#    ambiance = self.getConf()
#    return int(ambiance.get('general', 'thunder', fallback=constant.THUNDERSTORM_LEVEL_NONE))
#

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

  def setMode(self, mode):
    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)

      oConf.set('general', 'mode', str(isfile))
    
      with open(self.confFile, 'w') as configfile:
        oConf.write(configfile)

      return True

    return False;

  def getMode(self):
    mode = constant.STATE_MODE_REGULAR

    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)

      if oConf.has_option('general', 'mode'):
        mode = oConf.get('general', 'mode')
  
    return mode

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