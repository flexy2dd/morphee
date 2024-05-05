import datetime
import os
import codecs
import time
import math
import pprint

from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import sh1106

from PIL import ImageFont, ImageDraw, Image

from modules import constant
from modules import core

# ===========================================================================
# screen Class
# ===========================================================================

class screen():
  
  def __init__(self):
    i2cbus = i2c()
    self.device = sh1106(i2cbus, rotate=2)
    self.device.show()
    
    self.image = Image.new(self.device.mode, self.device.size)
    self.draw = ImageDraw.Draw(self.image)

    self.pulseStatus = 1
    self.pulsePos = 1
    self.fontSize = 10
    self.maxScreenLines = 6
    self.width = self.device.width
    self.height = self.device.height

    self.font = ImageFont.truetype('%s/../fonts/FreeSans.ttf' % os.path.dirname(__file__), self.fontSize)

    self.draw.text((0, 0), text="Init screen", font=self.font, fill='white')
    self.display()
      
    self.debugLines = []
    
    self.logoWifi100 = Image.open('%s/../icons/wifi-100.png' % os.path.dirname(__file__))
    self.logoWifi75  = Image.open('%s/../icons/wifi-75.png' % os.path.dirname(__file__))
    self.logoWifi50  = Image.open('%s/../icons/wifi-50.png' % os.path.dirname(__file__))
    self.logoWifi25  = Image.open('%s/../icons/wifi-25.png' % os.path.dirname(__file__))
    self.logoWifi0   = Image.open('%s/../icons/wifi-0.png' % os.path.dirname(__file__))
    
  def display(self):
    self.device.display(self.image)
    
  def cls(self, fill = 0):
    self.draw.rectangle(self.device.bounding_box, outline="black", fill="black")
    self.display()
    time.sleep(0.2)
    
  def setText(self, left, top, text, fill):
    self.draw.text((left, top), text, font=self.font, fill=fill)
  
  def setRect(self, left, top, width, height, outline, fill):
    self.draw.rectangle((left, top, width, height), outline, fill)
    
  def debug(self, text):
    self.debugLines.append(text)
    linesCount = len(self.debugLines) # how many lines
    
    if (linesCount > self.maxScreenLines):
      self.debugLines.pop(0)
      linesCount = len(self.debugLines)

    for index in range(linesCount):
      iTop = (index * self.fontSize)
      self.draw.text((0, iTop),  self.debugLines[index], fill="white")

    self.display()
    
  def countdown(self, step):
    self.draw.rectangle(self.device.bounding_box, outline="black", fill="black")
    font = ImageFont.truetype('%s/../fonts/digital-7mono.ttf' % os.path.dirname(__file__), 55)
    self.draw.text((40, 5), '{: >3}'.format(step) , font=font, fill=1)

    font = ImageFont.truetype('%s/../fonts/fontawesome-webfont.ttf' % os.path.dirname(__file__), 30)
    text = chr(constant.FONT_AWESOME_ICONS["fa-save"])
    self.draw.text((0, 12), text, font=font, fill=1)
    self.display()
    time.sleep(0.5)

  def picto(self, picto):

    self.draw.rectangle(self.device.bounding_box, outline="black", fill="black")
    font = ImageFont.truetype('%s/../fonts/fontawesome-webfont.ttf' % os.path.dirname(__file__), 50)
    text = chr(constant.FONT_AWESOME_ICONS["fa-" + picto])

    fontleft, fonttop, fontright, fontbottom = font.getbbox(text)
    boxleft, boxtop, boxright, boxbottom = self.device.bounding_box
    top = int((boxbottom - fontbottom) / 2)
    left = int((boxright - fontright) / 2)

    self.draw.text((left, top), text, font=font, fill=1)
    self.display()

  def clock(self):
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second             
    
    font = ImageFont.truetype('%s/../fonts/digital-7mono.ttf' % os.path.dirname(__file__), 55)
    
    self.draw.text((0, 0), now.strftime('%H') , font=font, fill=1)
    self.draw.text((65, 0), now.strftime('%M') , font=font, fill=1)
    
    if ((now.second % 2) == 0): # Toggle colon at 1Hz
      self.draw.text((46, 0), now.strftime(':') , font=font, fill=1)

  def remainingTime(self):

    #oCore = core.core()
    #remainingtime = oCore.getRemainingTime()
    remainingtime = '2024-04-30 21:00:00'
    remainingtime = datetime.datetime.strptime(remainingtime, '%Y-%m-%d %H:%M:%S')
    
    nowTime = datetime.datetime.now().replace(microsecond=0) 
    diffTime = remainingtime - nowTime
   
    d = diffTime.days  # days
    h = divmod(diffTime.seconds, 3600)  # hours
    m = divmod(h[1], 60)  # minutes
    s = m[1] # seconds

    hours = h[0] 
    if d>0:
      hours += d*24
    
    minutes = m[0]

    second = 0      
    if int(m[0])==0 and int(hours)==0 and int(s)>0:
      seconds = s

    font = ImageFont.truetype('%s/../fonts/digital-7mono.ttf' % os.path.dirname(__file__), 55)
    
    self.draw.text((0, 5), '{:0>2}'.format(hours) , font=font, fill=1)
    self.draw.text((65, 5), '{:0>2}'.format(minutes) , font=font, fill=1)
    self.draw.text((46, 5), ':' , font=font, fill=1)

  def pulse(self):

    step = 4

    if self.pulseStatus == 1:
      self.pulsePos = self.pulsePos + step
    else:
      self.pulsePos = self.pulsePos - step

    if self.pulsePos < 0:
      self.pulsePos = self.pulsePos + (step * 2)
      self.pulseStatus = 1

    if self.pulsePos > self.device.width:
      self.pulsePos = self.pulsePos - (step * 2)
      self.pulseStatus = 0

    self.draw.rectangle((0, self.device.height-1, self.device.width, self.device.height-1), outline="black", fill="black")
    self.draw.rectangle((self.pulsePos, self.device.height-1, self.pulsePos, self.device.height-1), outline="white", fill="white")
    self.display()
    
  def sleep(self, secondsWait = 5.0):
    affStart = time.time()
    milliseconds = float(secondsWait)*1000
    step = self.device.width / milliseconds

    self.draw.rectangle((0, self.device.height-1, self.device.width, self.device.height-1), outline="black", fill="black")
    self.display()

    while True:
      affCurrent=time.time()-affStart
      width = math.floor((affCurrent*step)*1000)

      self.draw.rectangle((0, self.device.height-2, width, self.device.height-2), fill="white")
      self.display()

      if affCurrent>secondsWait:
        self.cls()
        break