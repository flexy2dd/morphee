import RPi.GPIO as GPIO
import time
import math
import os
#import pygame
from PIL import ImageFont, ImageDraw, Image
from modules import constant
from modules import network
from modules import ambiance
from pprint import pprint

class menu():

  def __init__(self):
    self.swithRelease = 0
    self.genericOptionStep = 1
  
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

        if menu['options'][getin]['command'] == 'setRain':
          rotary.setRotateCallback(self.rotaryRotateGenericCall)
          self.genericOptionStep = 1
          self.swithRelease = 0
          self.setRain(screen)
          rotary.setRotateCallback(self.rotaryRotateCall)

        if menu['options'][getin]['command'] == 'setThunder':
          rotary.setRotateCallback(self.rotaryRotateGenericCall)
          self.genericOptionStep = 1
          self.swithRelease = 0
          self.setThunder(screen)
          rotary.setRotateCallback(self.rotaryRotateCall)

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

        if menu['options'][getin]['command'] == 'setSnooze':
          rotary.setRotateCallback(self.rotaryRotateGenericCall)
          self.swithRelease = 0
          self.setSnooze(screen)
          rotary.setRotateCallback(self.rotaryRotateCall)

        if menu['options'][getin]['command'] == 'setStop':
          rotary.setRotateCallback(self.rotaryRotateGenericCall)
          self.genericOptionStep = 1
          self.swithRelease = 0
          self.setStop(screen)
          rotary.setRotateCallback(self.rotaryRotateCall)

        screen.cls()
      elif menu['options'][getin]['type'] == constant.MENU_MENU:
            screen.cls() #clears previous screen on key press and updates display based on pos
            self.processmenu(screen, rotary, menu['options'][getin], menu) # display the submenu
            screen.cls() #clears previous screen on key press and updates display based on pos
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
  
  def setSnooze(self, screen):

    if self.swithRelease==1:
      self.swithRelease = 0
#      break

      time.sleep(0.10)

  def setRain(self, screen):
    screen.cls()
    screen.setText(0, 10, "Pluie", 1)

    oAmbiance = ambiance.ambiance()
    iRain = oAmbiance.getRain()

    left = 40
    top = 22
    logoRain = Image.open('%s/../icons/rain-%s.png' % (os.path.dirname(__file__), str(iRain)))
    screen.draw.rectangle((left, top, left+35, top+35), outline="white", fill="white")
    screen.draw.bitmap((left, top), logoRain, fill="black")
    screen.display()

    self.genericOptionMax = 3
    self.genericOptionMin = 0
    self.genericPos = iRain
    self.oldPos = iRain

    while(True):
      if self.oldPos != self.genericPos:
        logoRain = Image.open('%s/../icons/rain-%s.png' % (os.path.dirname(__file__), str(self.genericPos)))
        screen.draw.rectangle((left, top, left+35, top+35), outline="white", fill="white")
        screen.draw.bitmap((left, top), logoRain, fill="black")
        self.oldPos = self.genericPos
        screen.display()

      if self.swithRelease==1:
        self.swithRelease = 0
        oAmbiance.setRain(self.genericPos)
        break

      time.sleep(0.10)

  def setThunder(self, screen):
    screen.cls()
    screen.setText(0, 10, "Tonnerre", 1)

    oAmbiance = ambiance.ambiance()
    iThunder = oAmbiance.getThunder()

    left = 40
    top = 22
    logoThunder = Image.open('%s/../icons/thunder-%s.png' % (os.path.dirname(__file__), str(iThunder)))
    screen.draw.rectangle((left, top, left+35, top+35), outline="white", fill="white")
    screen.draw.bitmap((left, top), logoThunder, fill="black")
    screen.display()

    self.genericOptionMax = 3
    self.genericOptionMin = 0
    self.genericPos = iThunder
    self.oldPos = iThunder

    while(True):
      if self.oldPos != self.genericPos:
        logoThunder = Image.open('%s/../icons/thunder-%s.png' % (os.path.dirname(__file__), str(self.genericPos)))
        screen.draw.rectangle((left, top, left+35, top+35), outline="white", fill="white")
        screen.draw.bitmap((left, top), logoThunder, fill="black")
        self.oldPos = self.genericPos
        screen.display()

      if self.swithRelease==1:
        self.swithRelease = 0
        oAmbiance.setThunder(self.genericPos)
        break

      time.sleep(0.10)

  def setLight(self, screen):
    screen.cls()
    screen.setText(0, 10, "Eclairs", 1)
    screen.display()

    oAmbiance = ambiance.ambiance()
    iLight = oAmbiance.getLight()

    left = 40
    top = 22
    logoThunder = Image.open('%s/../icons/lightbulb-%s.png' % (os.path.dirname(__file__), str(iLight)))
    screen.draw.rectangle((left, top, left+35, top+35), outline="white", fill="white")
    screen.draw.bitmap((left, top), logoThunder, fill="black")
    screen.display()

    self.genericOptionMax = 1
    self.genericOptionMin = 0
    self.genericPos = iLight
    self.oldPos = iLight

    while(True):
      if self.oldPos != self.genericPos:
        logoThunder = Image.open('%s/../icons/lightbulb-%s.png' % (os.path.dirname(__file__), str(self.genericPos)))
        screen.draw.rectangle((left, top, left+35, top+35), outline="white", fill="white")
        screen.draw.bitmap((left, top), logoThunder, fill="black")
        self.oldPos = self.genericPos
        screen.display()

      if self.swithRelease==1:
        self.swithRelease = 0
        oAmbiance.setLight(self.genericPos)
        break

      time.sleep(0.10)

  def setVolume(self, screen):
    screen.cls()
    screen.setText(0, 10, "Volume", 1)

    oAmbiance = ambiance.ambiance()
    iVolume = oAmbiance.getVolume()

    volume = ((iVolume * 100.0) / 100) / 100    
    pygame.mixer.init();
    oTestSound = pygame.mixer.Sound('%s/../sounds/volume.wav' % os.path.dirname(__file__))
    oTestSound.set_volume(volume)
    oTestSound.play(1)

    left = 0
    top = 22
    font = ImageFont.truetype('%s/../fonts/FreeSans.ttf' % os.path.dirname(__file__), 45)
    screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
    screen.draw.text((left, top), str(iVolume), font=font, fill="white")

    screen.display()

    self.genericOptionMax = 100
    self.genericOptionMin = 0
    self.genericPos = iVolume
    self.oldPos = iVolume

    while(True):

      if self.oldPos != self.genericPos:
        screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
        screen.draw.text((left, top), str(self.genericPos), font=font, fill="white")
        self.oldPos = self.genericPos
        screen.display()
        volume = ((self.genericPos * 100.0) / 100) / 100
        oTestSound.set_volume(volume)

      if self.swithRelease==1:
        self.swithRelease = 0
        oTestSound.stop()
        oAmbiance.setVolume(self.genericPos)
        break

      time.sleep(0.10)

  def setStop(self, screen):
    screen.cls()
    oAmbiance = ambiance.ambiance()
    oAmbiance.stop()
    time.sleep(0.10)

  def setSnooze(self, screen):
    screen.cls()
    screen.setText(0, 10, "Temps", 1)

    oAmbiance = ambiance.ambiance()
    iSnooze = oAmbiance.getSnooze()

    left = 0
    top = 22
    font = ImageFont.truetype('%s/../fonts/FreeSans.ttf' % os.path.dirname(__file__), 30)
    screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
    screen.draw.text((left, top), str(iSnooze) + ' min', font=font, fill="white")

    screen.display()

    self.genericOptionMax = 100
    self.genericOptionMin = 0
    self.genericOptionStep = 15
    self.genericPos = iSnooze
    self.oldPos = iSnooze

    while(True):

      if self.oldPos != self.genericPos:
        screen.draw.rectangle((left, top, screen.device.width - 1, screen.device.height - 1), outline="black", fill="black")
        screen.draw.text((left, top), str(self.genericPos) + ' min', font=font, fill="white")
        self.oldPos = self.genericPos
        screen.display()

      if self.swithRelease==1:
        self.swithRelease = 0
        oAmbiance.setSnooze(self.genericPos)
        oAmbiance.start()
        break

      time.sleep(0.10)