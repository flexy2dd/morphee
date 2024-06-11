import RPi.GPIO as GPIO
import time
import math
import os
import logging
from PIL import ImageFont, ImageDraw, Image
from modules import constant
from modules import network
from modules import core
from modules import speak
from pprint import pprint

class menu():

  def __init__(self, **params):
    self.swithRelease = 0
    self.genericOptionStep = 1
    self.core = None
    self.logging = False
    self.verbose = False

    if 'core' in params:
      self.core = params['core']

    if 'logging' in params:
      self.logging = params['logging']
    else:
      logging_level: int = self.core.getDebugLevelFromText(self.core.readConf("level", "logging", 'INFO'))
      logging.basicConfig(level=int(logging_level))
  
  # This function displays the appropriate menu and returns the option selected
  def runmenu(self, screen, rotary, menu, parent):
  
    # work out what text to display as the last menu option
    if parent is None:
      lastoption = "Sortie"
    else:
      lastoption = "Retour %s" % parent['title']
  
    self.optioncount = len(menu['options']) # how many options in this menu
  
    self.pos = 0 #pos is the zero-based index of the hightlighted menu option. Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what opt$
    oldpos = None # used to prevent the screen being redrawn every time

    affStart = time.time()
    secondsWait = constant.MENU_WAIT_SECONDS
    totalWidth = screen.width
    waitStep = totalWidth / (float(secondsWait) * 1000)
    screen.draw.rectangle((0, screen.height-1, totalWidth, screen.height-1), 0, 1)
  
    # Loop until return key is pressed
    while True:
      affCurrent = time.time() - affStart
      waitWidth = (affCurrent * waitStep) * 1000
      screen.draw.rectangle((0, screen.height-1, waitWidth, screen.height-1), 0, 0)
      screen.display()
  
      if self.pos != oldpos:
        affStart = time.time()
        screen.draw.rectangle((0, screen.height-1, totalWidth, screen.height-1), 0, 1)
        oldpos = self.pos
        screen.setText(0, 0, menu['title'], fill="white")
  
        # Display all the menu items, showing the 'pos' item highlighted
        for index in range(self.optioncount):
          iTop = 10 + (index * screen.fontSize)
  
          if self.pos == index:
            screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 1, 1)
            screen.setText(0, iTop, "%d - %s" % (index+1, menu['options'][index]['title']), 0)
          else:
            screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 0, 0)
            screen.setText(0, iTop, "%d - %s" % (index+1, menu['options'][index]['title']), 1)
  
        # Now display Exit/Return at bottom of menu
        iTop = 10 + (self.optioncount * screen.fontSize)
        if self.pos == self.optioncount:
          screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 1, 1)
          screen.setText(0, iTop, "%d - %s" % (self.optioncount+1, lastoption), 0)
        else:
          screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 0, 0)
          screen.setText(0, iTop, "%d - %s" % (self.optioncount+1, lastoption), 1)
  
        screen.display()
        # finished updating screen
  
      if affCurrent>secondsWait:
        return -1

      if self.swithRelease==1:
        self.swithRelease = 0
        break
  
    # return index of the selected item
    return self.pos

  def rotaryRotateGenericCall(self, direction):
    if direction=='left':
      if self.genericPos < self.genericOptionMax:
        self.genericPos += self.genericOptionStep
      else:
        self.genericPos = self.genericOptionMax
    elif direction=='right':
      if self.genericPos > self.genericOptionMin:
        self.genericPos += -self.genericOptionStep
      else:
        self.genericPos = self.genericOptionMin

  def rotaryRotateCall(self, direction):
    if direction=='left':
      if self.pos < self.optioncount:
        self.pos += 1
      else:
        self.pos = self.optioncount
    elif direction=='right':
      if self.pos > 0:
        self.pos += -1
      else:
        self.pos = 0
  
  def rotarySwitchCall(self, switchStatus):
    if switchStatus=='release':
      self.swithRelease = 1
  
  # This function calls showmenu and then acts on the selected item
  def processmenu(self, screen, rotary, menu, parent=None):
    self.optioncount = len(menu['options'])
    self.exitmenu = False
    
    rotary.setSwitchCallback(self.rotarySwitchCall)
    rotary.setRotateCallback(self.rotaryRotateCall)
    rotary.triggerEnable()
    
    while not self.exitmenu: #Loop until the user exits the menu
      getin = self.runmenu(screen, rotary, menu, parent)
      if getin == self.optioncount:
         self.exitmenu = True
      elif getin == -1:
        self.exitmenu = True
      elif menu['options'][getin]['type'] == 'viewInfos':
        self.viewInfos(screen)
      elif menu['options'][getin]['type'] == constant.MENU_COMMAND:

        if menu['options'][getin]['command'] == 'setLight':
          rotary.setRotateCallback(self.rotaryRotateGenericCall)
          self.genericOptionStep = 1
          self.swithRelease = 0
          self.setLight(screen)
          rotary.setRotateCallback(self.rotaryRotateCall)

        if menu['options'][getin]['command'] == 'setVolume':
          rotary.setRotateCallback(self.rotaryRotateGenericCall)
          self.genericOptionStep = 1
          self.swithRelease = 0
          self.setVolume(screen)
          rotary.setRotateCallback(self.rotaryRotateCall)

        if menu['options'][getin]['command'] == 'setSpeakVolume':
          rotary.setRotateCallback(self.rotaryRotateGenericCall)
          self.genericOptionStep = 1
          self.swithRelease = 0
          self.setSpeakVolume(screen)
          rotary.setRotateCallback(self.rotaryRotateCall)

        screen.cls()
      elif menu['options'][getin]['type'] == constant.MENU_MENU:
            screen.cls()
            self.processmenu(screen, rotary, menu['options'][getin], menu)
            screen.cls()
      elif menu['options'][getin]['type'] == constant.MENU_EXIT:
            self.exitmenu = True

    rotary.triggerDisable()
  
  def viewInfos(self, screen):
    screen.cls()
    screen.setText(0, 10, "ip: %s" % network.get_lan_ip(), 1)

    left = 40
    top = 22
    
    screen.draw.rectangle((left, top, left+35, top+35), outline="white", fill="white")

    level = int(network.get_wifi_signal())
    if level>0 and level<=25:
      screen.draw.bitmap((left, top), screen.logoWifi25, fill="black")
    elif level>25 and level<=50:
      screen.draw.bitmap((left, top), screen.logoWifi50, fill="black")
    elif level>50 and level<=75:
      screen.draw.bitmap((left, top), screen.logoWifi75, fill="black")
    elif level>75:
      screen.draw.bitmap((left, top), screen.logoWifi100, fill="black")
    else:
      screen.draw.bitmap((left, top), screen.logoWifi0, fill="black")

    screen.display()

    while(True):
      if self.swithRelease==1:
        self.swithRelease = 0
        break

      time.sleep(0.10)
  
  def setLight(self, screen):
    screen.cls()
    screen.setText(0, 10, "Lumières", 1)
    screen.display()

    affStart = time.time()
    secondsWait = constant.MENU_WAIT_SECONDS
    waitStep = screen.width / (float(secondsWait) * 1000)

    self.genericOptionMax = 1
    self.genericOptionMin = 0
    self.genericPos = self.core.getLight()
    self.oldPos = self.core.getLight()
    
    left = 40
    top = 22
    logoLight = Image.open('%s/../icons/lightbulb-%s.png' % (os.path.dirname(__file__), str(self.genericPos)))
    screen.draw.rectangle((left, top, left+35, top+35), outline="white", fill="white")
    screen.draw.bitmap((left, top), logoLight, fill="black")
    screen.display()

    while(True):

      affCurrent = time.time() - affStart
      waitWidth = (affCurrent * waitStep) * 1000
      screen.draw.rectangle((0, screen.height-1, screen.width, screen.height-1), 0, 0)

      if self.oldPos != self.genericPos:
        affStart = time.time()
        logoLight = Image.open('%s/../icons/lightbulb-%s.png' % (os.path.dirname(__file__), str(self.genericPos)))
        screen.draw.rectangle((left, top, left+35, top+35), outline="white", fill="white")
        screen.draw.bitmap((left, top), logoLight, fill="black")
        self.oldPos = self.genericPos
        self.core.setLight(self.genericPos)

      if affCurrent>secondsWait:
        return -1

      if self.swithRelease==1:
        self.swithRelease = 0
        self.core.setLight(self.genericPos)
        return 0
        break

      screen.display()

      time.sleep(0.10)

  def setVolume(self, screen):
    screen.cls()
    screen.setText(0, 10, "Volume", 1)

    affStart = time.time()
    secondsWait = constant.MENU_WAIT_SECONDS
    waitStep = screen.width / (float(secondsWait) * 1000)

    self.genericOptionMax = 100
    self.genericOptionMin = 0
    self.genericPos = self.core.getGeneralVolume()
    self.oldPos = self.genericPos

    left = 0
    top = 22
    font = ImageFont.truetype('%s/../fonts/FreeSans.ttf' % os.path.dirname(__file__), 45)
    screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
    screen.draw.text((left, top), str(self.genericPos), font=font, fill="white")

    screen.display()

    while(True):

      affCurrent = time.time() - affStart
      waitWidth = (affCurrent * waitStep) * 1000
      screen.draw.rectangle((0, screen.height-1, screen.width, screen.height-1), 0, 0)

      if self.oldPos != self.genericPos:
        affStart = time.time()
        screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
        screen.draw.text((left, top), str(self.genericPos), font=font, fill="white")
        self.oldPos = self.genericPos

        self.core.setGeneralVolume(self.genericPos)

      if affCurrent>secondsWait:
        return -1

      if self.swithRelease==1:
        self.swithRelease = 0
        self.core.setGeneralVolume(self.genericPos)
        return 0
        break

      screen.display()

      time.sleep(0.10)

  def setSpeakVolume(self, screen):
    screen.cls()
    screen.setText(0, 10, "Volume", 1)

    affStart = time.time()
    secondsWait = constant.MENU_WAIT_SECONDS
    waitStep = screen.width / (float(secondsWait) * 1000)

    oSpeak = speak.speak()
    oSpeak.verbose = True

    self.genericOptionMax = 100
    self.genericOptionMin = 0
    self.genericPos = self.core.getSpeakVolume()
    self.oldPos = self.genericPos

    left = 0
    top = 22
    font = ImageFont.truetype('%s/../fonts/FreeSans.ttf' % os.path.dirname(__file__), 45)
    screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
    screen.draw.text((left, top), str(self.genericPos), font=font, fill="white")

    screen.display()

    while(True):

      affCurrent = time.time() - affStart
      waitWidth = (affCurrent * waitStep) * 1000
      screen.draw.rectangle((0, screen.height-1, screen.width, screen.height-1), 0, 0)

      if self.oldPos != self.genericPos:
        affStart = time.time()
        screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
        screen.draw.text((left, top), str(self.genericPos), font=font, fill="white")
        self.oldPos = self.genericPos
        oSpeak.say("Test volume...", self.genericPos, True)
        self.core.setSpeakVolume(self.genericPos)

      if affCurrent>secondsWait:
        oSpeak.stop()
        return -1

      if self.swithRelease==1:
        self.swithRelease = 0
        self.core.setSpeakVolume(self.genericPos)
        oSpeak.stop()
        return 0
        break

      screen.display()

      time.sleep(0.10)

  def setScreenContrast(self, screen):
    screen.cls()
    screen.setText(0, 10, "Contraste", 1)

    affStart = time.time()
    secondsWait = constant.MENU_WAIT_SECONDS
    waitStep = screen.width / (float(secondsWait) * 1000)

    self.genericOptionMax = 255
    self.genericOptionMin = 0
    self.genericPos = self.core.getScreenContrast()
    self.oldPos = self.genericPos

    left = 0
    top = 22
    font = ImageFont.truetype('%s/../fonts/FreeSans.ttf' % os.path.dirname(__file__), 45)
    screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
    screen.draw.text((left, top), str(self.genericPos), font=font, fill="white")

    screen.display()

    while(True):

      affCurrent = time.time() - affStart
      waitWidth = (affCurrent * waitStep) * 1000
      screen.draw.rectangle((0, screen.height-1, screen.width, screen.height-1), 0, 0)

      if self.oldPos != self.genericPos:
        affStart = time.time()
        screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
        screen.draw.text((left, top), str(self.genericPos), font=font, fill="white")
        self.oldPos = self.genericPos
        screen.contrast(self.genericPos)
        self.core.setScreenContrast(self.genericPos)

      if affCurrent>secondsWait:
        return -1

      if self.swithRelease==1:
        self.swithRelease = 0
        self.core.setScreenContrast(self.genericPos)
        return 0
        break

      screen.display()

      time.sleep(0.10)

  def setAnimBrightness(self, screen):
    screen.cls()
    screen.setText(0, 10, "Luminosité", 1)

    affStart = time.time()
    secondsWait = constant.MENU_WAIT_SECONDS
    waitStep = screen.width / (float(secondsWait) * 1000)

    self.genericOptionMax = 100
    self.genericOptionMin = 0
    self.genericPos = self.core.getAnimBrightness()
    self.oldPos = self.genericPos

    left = 0
    top = 22
    font = ImageFont.truetype('%s/../fonts/FreeSans.ttf' % os.path.dirname(__file__), 45)
    screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
    screen.draw.text((left, top), str(self.genericPos), font=font, fill="white")

    screen.display()

    while(True):

      affCurrent = time.time() - affStart
      waitWidth = (affCurrent * waitStep) * 1000
      screen.draw.rectangle((0, screen.height-1, screen.width, screen.height-1), 0, 0)

      if self.oldPos != self.genericPos:
        affStart = time.time()
        screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
        screen.draw.text((left, top), str(self.genericPos), font=font, fill="white")
        self.oldPos = self.genericPos
        self.core.setAnimBrightness(self.genericPos)

      if affCurrent>secondsWait:
        return -1

      if self.swithRelease==1:
        self.swithRelease = 0
        self.core.setAnimBrightness(self.genericPos)
        return 0
        break

      screen.display()

      time.sleep(0.10)
