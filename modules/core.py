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

  def getFilePid(self):
    return '%s/../%s' % (os.path.dirname(__file__), constant.CORE_PID)

  def getFileConf(self):
    return '%s/../%s' % (os.path.dirname(__file__), constant.CORE_CONF)

  def getRootPath(self):
    return '%s/../' % (os.path.dirname(__file__))

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
    mode = 'regular'

    if os.path.isfile(self.confFile):
      oConf = configparser.ConfigParser()
      oConf.read(self.confFile)

      if oConf.has_option('general', 'mode'):
        mode = oConf.get('general', 'mode')
  
    return mode

  def getAmbiance(self):
    if os.path.isfile(self.ambianceConf):
      oAmbiance = configparser.ConfigParser()
      oAmbiance.read(self.ambianceConf)
  
      if oAmbiance.has_option('general', 'title'):
        generalTitle = oAmbiance.get('general', 'title')
  
      return oAmbiance
  
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
#    if os.path.isfile(self.ambianceConf):
#      ambiance = configparser.ConfigParser()
#      ambiance.read(self.ambianceConf)
#
#      if int(rain) in [constant.RAIN_LEVEL_NONE, constant.RAIN_LEVEL_LIGHT, constant.RAIN_LEVEL_MODERATE, constant.RAIN_LEVEL_HEAVY]:
#        ambiance.set('general', 'rain', str(rain))
#
#        with open(self.ambianceConf, 'w') as configfile:
#          ambiance.write(configfile)
#
#        return True
#
#    return False;
#
#  def getRain(self):
#    ambiance = self.getAmbiance()
#    return int(ambiance.get('general', 'rain', fallback=constant.RAIN_LEVEL_NONE))
#
#  def setThunder(self, thunderstorm):
#    if os.path.isfile(self.ambianceConf):
#      ambiance = configparser.ConfigParser()
#      ambiance.read(self.ambianceConf)
#
#      if int(thunderstorm) in [constant.THUNDERSTORM_LEVEL_NONE, constant.THUNDERSTORM_LEVEL_LIGHT, constant.THUNDERSTORM_LEVEL_MODERATE, constant.THUNDERSTORM_LEVEL_HEAVY]:
#        ambiance.set('general', 'thunder', str(thunderstorm))
#
#        with open(self.ambianceConf, 'w') as configfile:
#          ambiance.write(configfile)
#
#        return True
#
#    return False;
#
#  def getThunder(self):
#    ambiance = self.getAmbiance()
#    return int(ambiance.get('general', 'thunder', fallback=constant.THUNDERSTORM_LEVEL_NONE))
#
#  def setLight(self, thunderlight):
#    if os.path.isfile(self.ambianceConf):
#      ambiance = configparser.ConfigParser()
#      ambiance.read(self.ambianceConf)
#
#      if int(thunderlight) in [constant.THUNDERLIGHT_ON, constant.THUNDERLIGHT_OFF]:
#        ambiance.set('general', 'light', str(thunderlight))
#
#        with open(self.ambianceConf, 'w') as configfile:
#          ambiance.write(configfile)
#
#        return True
#
#    return False;
#
#  def getLight(self):
#    ambiance = self.getAmbiance()
#    return int(ambiance.get('general', 'light', fallback=constant.THUNDERLIGHT_ON))

  def setVolume(self, volume):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      ambiance.set('general', 'volume', str(volume))
    
      with open(self.ambianceConf, 'w') as configfile:
        ambiance.write(configfile)

      return True

    return False;

  def getVolume(self):
    ambiance=self.getAmbiance()
    return int(ambiance.get('general', 'volume', fallback='30'))

#  def setSnooze(self, snooze):
#    if os.path.isfile(self.ambianceConf):
#      ambiance = configparser.ConfigParser()
#      ambiance.read(self.ambianceConf)
#
#      ambiance.set('general', 'snooze', str(snooze))
#    
#      with open(self.ambianceConf, 'w') as configfile:
#        ambiance.write(configfile)
#
#      return True
#
#    return False;
#
#  def getSnooze(self):
#    ambiance=self.getAmbiance()
#    return int(ambiance.get('general', 'snooze', fallback='30'))

  def start(self):
    if os.path.exists(self.getFilePid()):
      os.remove(self.getFilePid())
  
    iSnooze = self.getSnooze()
    unixTime = time.mktime(datetime.datetime.now().replace(microsecond=0).timetuple())
    f = open(self.getFilePid(), "w")
    f.write(str(unixTime + (iSnooze * 60)))
    f.close()
    
    return True
    
  def stop(self):
    if os.path.exists(self.getFilePid()):
      os.remove(self.getFilePid())

    #pygame.mixer.music.fadeout(4000)
    #pygame.mixer.music.stop()

    return True

#  def thunderToStr(self, iThunder):  
#    switcher = {
#        1: "light",
#        2: "moderate",
#        3: "heavy",
#    }
#    return switcher.get(iThunder, "none")
    
#  def loadEvents(self):
#    oAmbianceConf = configparser.ConfigParser()
#    oAmbianceConf.read(self.ambianceConf)
#
#    eventsDict = {}
#
#    self.currentThunderLevel = int(oAmbianceConf.get('general', 'thunder', fallback=constant.THUNDERSTORM_LEVEL_NONE))
#    
#    if self.currentThunderLevel>0:
#      iAmbianceVolume = int(oAmbianceConf.get('general', 'volume', fallback=50))
#      oThunderlight = thunderlight.thunderlight()
#      
#      # default values
#      fDefaultVolume = 100.00
#      iDefaultLightOffset = 0
#      iDefaultLightDelay = int(oThunderlight.getDelayFactor())
#      iDefaultLightStrike = int(oThunderlight.getStrikeFactor())
#      iDefaultLightBright = int(oThunderlight.getBrightFactor())
#      
#      oEventDefaultConf = configparser.ConfigParser()
#      eventFileDefaultConf = 'sounds/thunder/thunder.conf'
#      if os.path.isfile(eventFileDefaultConf):
#        oEventDefaultConf.read(eventFileDefaultConf)
#        fDefaultVolume = oEventDefaultConf.getfloat('general-' + str(self.currentThunderLevel), 'volume', fallback=fDefaultVolume)
#        iDefaultLightOffset = oEventDefaultConf.getint('light-' + str(self.currentThunderLevel), 'offset', fallback=iDefaultLightOffset)
#        iDefaultLightDelay = oEventDefaultConf.getint('light-' + str(self.currentThunderLevel), 'delay', fallback=iDefaultLightDelay)
#        iDefaultLightStrike = oEventDefaultConf.getint('light-' + str(self.currentThunderLevel), 'force', fallback=iDefaultLightStrike)
#        iDefaultLightBright = oEventDefaultConf.getint('light-' + str(self.currentThunderLevel), 'bright', fallback=iDefaultLightBright)
#      
#      regexp = r".*/(thunder-" + self.thunderToStr(self.currentThunderLevel) + "-.*)\.(wav|mp3)"
#      eventIndex = 0
#      for file in glob.glob('sounds/thunder/*'):
#        result = re.match(regexp, str(file))
#        if result is not None:
#      
#          self.debug('find event ' + file)
#      
#          fileRoot = result.groups()[0]
#          fileExt = result.groups()[1]
#      
#          oEventConf = configparser.ConfigParser()
#      
#          eventFileConf = 'sounds/thunder/' + fileRoot + '.conf'
#          if os.path.isfile(eventFileConf):
#            oEventConf.read(eventFileConf)
#      
#          fVolume = fDefaultVolume
#          if oEventConf.has_option('general', 'volume'):
#            fVolume = oEventConf.getfloat('general', 'volume', fallback=fDefaultVolume)
#          
#          iVolume = ((iAmbianceVolume * fVolume) / 100) / 100
#      
#          iLightOffset = int(oEventConf.get('light', 'offset', fallback=iDefaultLightOffset))
#          iLightDelay = int(oEventConf.get('light', 'delay', fallback=iDefaultLightDelay))
#          iLightStrike = int(oEventConf.get('light', 'force', fallback=iDefaultLightStrike))
#          iLightBright = int(oEventConf.get('light', 'bright', fallback=iDefaultLightBright))
#          
#          eventFile = '%s/../sounds/thunder/%s.%s' % (os.path.dirname(__file__), fileRoot, fileExt)
#          self.debug('load event ' + eventFile)
#          
#          #oEvent = pygame.mixer.Sound(eventFile)
#          #oEvent.set_volume(iVolume)
#      
#          #self.debug('..loaded ' + str(eventIndex) + '(duration:' + str(oEvent.get_length()) + ', volume:' + str(iVolume) + ')')
#          #eventsDict[eventIndex] = {'file' : eventFile, 'oEvent' : oEvent, 'duration' : oEvent.get_length(), 'volume' : iVolume, 'lightOffset': iLightOffset, 'lightDelay': iLightDelay, 'lightStrike': iLightStrike, 'lightBright': iLightBright}
#          
#          eventIndex += 1
#        else:
#          self.debug('..not found')
#
#    self.debug('has ' + str(len(eventsDict)) + ' event(s) loaded')
#    
#    return eventsDict
  
#  def rainToStr(self, iRain):
#    switcher = {
#        1: "light",
#        2: "moderate",
#        3: "heavy",
#    }
#    return switcher.get(iRain, "none")

  def playBackground(self):
    oAmbianceConf = configparser.ConfigParser()
    oAmbianceConf.read(self.ambianceConf)

    self.currentRainLevel = int(oAmbianceConf.get('general', 'rain', fallback=constant.RAIN_LEVEL_NONE))
    
    if self.currentRainLevel>0:

      iAmbianceVolume = int(oAmbianceConf.get('general', 'volume', fallback=50))
      
      fDefaultVolume = 100.00
      iDefaultDeltaMin = constant.CORE_DELTAMIN
      iDefaultDeltaMax = constant.CORE_DELTAMAX
      oDefaultConf = configparser.ConfigParser()
      fileDefaultConf = 'sounds/rain/rain.conf'
      if os.path.isfile(fileDefaultConf):
        oDefaultConf.read(fileDefaultConf)
        fDefaultVolume = oDefaultConf.getfloat('general-' + str(self.currentRainLevel), 'volume', fallback=fDefaultVolume)
        iDefaultDeltaMin = oDefaultConf.getint('general-' + str(self.currentRainLevel), 'deltaMin', fallback=iDefaultDeltaMin)
        iDefaultDeltaMax = oDefaultConf.getint('general-' + str(self.currentRainLevel), 'deltaMax', fallback=iDefaultDeltaMax)

      regexp = r".*/(rain-" + self.rainToStr(self.currentRainLevel) + "-.*)\.(wav|mp3)"
      rainFiles = []
      for file in glob.glob('sounds/rain/*'):
        result = re.match(regexp, str(file))
        if result is not None:
          rainFiles.append({'file': file, 'root': result.groups()[0], 'ext': result.groups()[1]})
      
      if len(rainFiles) <= 0:
        return False
      
      iIdx = 0
      if len(rainFiles) > 1:
        iIdx = random.randrange(0, len(rainFiles)-1)
      
      rainFile = rainFiles[iIdx]
      
      oBackgroundConf = configparser.ConfigParser()
      
      backgroundFileConf = 'sounds/rain/' + rainFile['root'] + '.conf'
      if os.path.isfile(backgroundFileConf):
        oBackgroundConf.read(backgroundFileConf)
      
      fVolume = fDefaultVolume
      if oBackgroundConf.has_option('general', 'volume'):
        fVolume = oBackgroundConf.getfloat('general', 'volume', fallback=fDefaultVolume)
      
      iVolume = ((iAmbianceVolume * fVolume) / 100) / 100
      
      self.currentDeltaMin = oBackgroundConf.getint('general', 'deltaMin', fallback=iDefaultDeltaMin)
      self.currentDeltaMax = oBackgroundConf.getint('general', 'deltaMax', fallback=iDefaultDeltaMax)
      
      backgroundFile = '%s/../sounds/rain/%s.%s' % (os.path.dirname(__file__), rainFile['root'], rainFile['ext'])
      self.debug('load background ' + backgroundFile)
      
      if os.path.isfile(backgroundFile):
        #oBackground = pygame.mixer.Sound(backgroundFile)
      
        self.debug('play background ' + backgroundFile + ' (volume:' + str(iVolume) + ')')
      
        #oBackground.set_volume(iVolume)
        #oBackground.play(-1)
