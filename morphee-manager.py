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
import RPi.GPIO as GPIO
import board
import random
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
from pathlib import Path
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from PIL import ImageFont, ImageDraw, Image
from luma.core.render import canvas

from modules import core
from modules import speak
from modules import network
from modules import menu
from modules import screen
from modules import rotary
from modules import constant
from modules import rfid
from modules import animator
from modules import mopidy

# ===========================================================================
# Menu definition
# ===========================================================================
menu_data = {
  'title': "General", 'type': constant.MENU_MENU,
  'options':[
    { 'title': "Snooze", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Lancer", 'type': constant.MENU_COMMAND, 'command': 'setSnooze', 'enable': True },
        { 'title': "Arreter", 'type': constant.MENU_COMMAND, 'command': 'setStop', 'enable': True },
      ]
    },
    { 'title': "Ambiance", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Pluie", 'type': constant.MENU_COMMAND, 'command': 'setRain', 'enable': True },
        { 'title': "Orage", 'type': constant.MENU_COMMAND, 'command': 'setThunder', 'enable': True },
        { 'title': "Eclairs", 'type': constant.MENU_COMMAND, 'command': 'setLight', 'enable': True },
        { 'title': "Volume", 'type': constant.MENU_COMMAND, 'command': 'setVolume', 'enable': True },
      ]
    },
    { 'title': "Parametres", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Volume", 'type': constant.MENU_COMMAND, 'command': 'setVolume', 'enable': True },
        { 'title': "Informations", 'type': 'viewInfos', 'enable': True}
#        { 'title': "Heure", 'type': constant.MENU_COMMAND, 'command': 'setTime', 'enable': True },
#        { 'title': "Date", 'type': constant.MENU_COMMAND, 'command': 'setDate', 'enable': True },
      ]
    },
  ]
}

currentMode = 'regular'

# ===========================================================================
# Param
# ===========================================================================
parser = argparse.ArgumentParser(description="Morphe manager service")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
parser.add_argument("-V", "--volume", help="volume (0 > 100)", type=int)
parser.add_argument("-s", "--start", help="start mode", action='store_true')
args = parser.parse_args()

# ===========================================================================
# Import config
# ===========================================================================
oCore = core.core()
#oCore.readGeneralConf(sKey, mDefault)
scriptName = Path(__file__).stem

# ===========================================================================
# Logging
# ===========================================================================
logging_level: int = oCore.readConf("level", "logging", 20)
logging_path: str = oCore.readConf("path", "logging", '.')
logging.basicConfig(filename=logging_path + '/' + scriptName + '.log', level=int(logging_level))

# ===========================================================================
# MQTT
# ===========================================================================

def on_publish(client, userdata, mid, reason_code, properties):
  if args.verbose:
    print("MQTT Publish")
    print(userdata, mid, reason_code, properties)

def on_log(client, userdata, level, buf):
  if args.verbose:
    print("MQTT Log " + buf)
  
  logging.debug("MQTT Log " + buf)

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
  if args.verbose:
    print("MQTT Disconnect " + reason_code)

  logging.info("MQTT Disconnect " + reason_code)

def on_connect(client, userdata, flags, reason_code, properties):
  if args.verbose:
    print("MQTT Connection Success")
    print("MQTT Subscribe")
  
  logging.info("Connection Success")
  logging.info("MQTT Subscribe")

  #client.subscribe(constant.MQTT_TOPIC_ANIMATION_START, 2)
  #client.subscribe(constant.MQTT_TOPIC_ANIMATION_STOP, 2)
  #client.subscribe(constant.MQTT_TOPIC_MODE_SET, 2)
  client.subscribe(constant.MQTT_TOPIC_CARTE_ENCODE)

  if reason_code == 0:
    logging.info("MQTT Connection Success")
  else:
    logging.critical("Failed to connect, return code %d\n", reason_code)

def on_message(client, userdata, msg):
  global currentMode
    
  if args.verbose:
    print("MQTT onMessage")
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

  logging.info(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

  if msg.topic == constant.MQTT_TOPIC_MODE_SET:

    payload = json.loads(msg.payload.decode("utf-8"))
    currentMode = payload["mode"]
    time.sleep(0.5)
    
    #beginloopTime = time.time()
    #loopTime = time.time()

  elif msg.topic == constant.MQTT_TOPIC_CARTE_ENCODE:

    if args.verbose:
      print("Set mode to encode")
    
    logging.info('Set mode to encode')

    currentMode = "encode"

    payload = json.loads(msg.payload.decode("utf-8"))
    #currentMode = payload["mode"]

    if args.verbose:
      print('Launch animation')
    
    logging.info('Launch animation')

#    publish.single(
#      constant.MQTT_TOPIC_ANIMATION_START, 
#      json.dumps({
#        "name": "blink",
#        "brightness": 10,
#        "time": 120,
#        "parameters": {
#          "speed": 0.5, 
#          "color": "ORANGE"
#        }
#      }),
#      hostname=str(constant.MQTT_HOST), 
#      port=int(constant.MQTT_PORT), 
#      client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
#    )
#    time.sleep(1)
    
    oSpeak.say("Veuillez insérer la carte dans le lecteur...")

    if args.verbose:
      print('Try write card')
    
    logging.info('Try write card')

    textEncode = payload['style'] + '|' + payload['url']

    encoded = False

    id, text_in = oRfid.reader.write_no_block(textEncode)

    loopTimeout = constant.CARD_ENCODE_TIMEOUT
    loopStartTime = time.time()
    loopTimeoutTime = time.time() + loopTimeout
    while time.time() <= loopTimeoutTime:
      loopStep = int(loopTimeoutTime-time.time())
      oScreen.countdown(loopStep+1)

      if id:
        encoded = True
        break

      id, text_in = oRfid.reader.write_no_block(textEncode)    

    if encoded:

      if args.verbose:
        print('Card is encoded with ' + textEncode)

      logging.info('Card is encoded ' + textEncode)

      oScreen.picto('check-circle');

      msgs = [{'topic': constant.MQTT_TOPIC_CARTE_ENCODED, 'payload': '{"encoded": True}', "qos": 0, "retain": False}, 
              {'topic': constant.MQTT_TOPIC_ANIMATION_STOP, 'payload': "{}", "qos": 0, "retain": False}]
      publish.multiple(
        msgs,
        hostname=str(constant.MQTT_HOST), 
        port=int(constant.MQTT_PORT), 
        client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
      )
      time.sleep(0.5)

      publish.single(
        constant.MQTT_TOPIC_ANIMATION_START, 
        json.dumps({
          "name": "blink",
          "brightness": 10,
          "time": 4,
          "parameters": {
            "speed": 0.5, 
            "color": "GREEN"
          }
        }),
        hostname=str(constant.MQTT_HOST), 
        port=int(constant.MQTT_PORT), 
        client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
      )

      oSpeak.say("La carte est encodée !")

    else:

      if args.verbose:
        print('Card is NOT encoded')

      logging.info('Card is NOT encoded')

      oScreen.picto('times-circle');

      msgs = [{'topic': constant.MQTT_TOPIC_CARTE_ENCODED, 'payload': '{"encoded": False}', "qos": 0, "retain": False}, 
              {'topic': constant.MQTT_TOPIC_ANIMATION_STOP, 'payload': '{}', "qos": 0, "retain": False}]
      publish.multiple(
        msgs,
        hostname=str(constant.MQTT_HOST), 
        port=int(constant.MQTT_PORT), 
        client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
      )

      publish.single(
        constant.MQTT_TOPIC_ANIMATION_START, 
        json.dumps({
          "name": "blink",
          "brightness": 10,
          "time": 4,
          "parameters": {
            "speed": 0.5, 
            "color": "RED"
          }
        }),
        hostname=str(constant.MQTT_HOST), 
        port=int(constant.MQTT_PORT), 
        client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
      )

      oSpeak.say("La carte n'a pas pu être encodée !")

    time.sleep(5)

    publish.single(
      constant.MQTT_TOPIC_ANIMATION_STOP, 
      json.dumps({}),
      hostname=str(constant.MQTT_HOST), 
      port=int(constant.MQTT_PORT), 
      client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
    )
    
    oScreen.cls();
    currentMode = "regular"

# connect to mqtt server
oMqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, f"mqtt-{scriptName}-{random.randint(0, 1000)}")
oMqttClient.on_connect = on_connect
oMqttClient.on_message = on_message
oMqttClient.on_disconnect = on_disconnect
oMqttClient.on_publish = on_publish
oMqttClient.on_log = on_log
oMqttClient.enable_logger = logging
if args.verbose:
  print('Start MQTT on ' + str(constant.MQTT_HOST) + ':' + str(constant.MQTT_PORT))

logging.info('Start MQTT on ' + str(constant.MQTT_HOST) + ':' + str(constant.MQTT_PORT))

oMqttClient.connect(str(constant.MQTT_HOST), int(constant.MQTT_PORT))
oMqttClient.loop_start()

publish.single(
  constant.MQTT_TOPIC_ANIMATION_START, 
  json.dumps({
    "name": "chase",
    "brightness": 10,
    "time": 5,
    "parameters": {
      "speed": 0.05, 
      "color": "WHITE",
      "size": 3,
      "spacing": 6,
      "reverse": False
    }
  }),
  hostname=str(constant.MQTT_HOST), 
  port=int(constant.MQTT_PORT), 
  client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
)

# ===========================================================================
# Mopidy
# ===========================================================================
oMopidy = mopidy.mopidy()
oMopidy.verbose = args.verbose
oMopidy.logging = logging

# ===========================================================================
# Speak
# ===========================================================================
oSpeak = speak.speak()
oSpeak.verbose = args.verbose
oSpeak.logging = logging
oSpeak.say("Initialisation en cours...")

# ===========================================================================
# Screen
# ===========================================================================
oScreen = screen.screen()
oScreen.cls()
oScreen.debug('init clock')
oScreen.debug("ip: %s" % network.get_lan_ip())
oScreen.sleep(2)
oScreen.cls()

# ===========================================================================
# Rfid
# ===========================================================================
def rfidRemove(id, text):
  if args.verbose:
    print('Remove to ' + id + ' : ' + text)

  logging.info('Remove to ' + id + ' : ' + text)
      
  publish.single(
    constant.MQTT_TOPIC_RFID, 
    json.dumps({
      "action": "remove",
      "text": text,
      "id": id
    }),
    hostname=str(constant.MQTT_HOST), 
    port=int(constant.MQTT_PORT), 
    client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
  )

def rfidInsert(id, text):
  if args.verbose:
    print('Insert to ' + id + ' : ' + text)

  publish.single(
    constant.MQTT_TOPIC_RFID, 
    json.dumps({
      "action": "insert",
      "text": text,
      "id": id
    }),
    hostname=str(constant.MQTT_HOST), 
    port=int(constant.MQTT_PORT), 
    client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
  )

def rfidChange(id, text, idOld, textOld):
  if args.verbose:
    print('change to ' + id + ' : ' + text)

  publish.single(
    constant.MQTT_TOPIC_RFID, 
    json.dumps({
      "action": "change",
      "text": text,
      "id": id,
      "old": {
        "text": textOld,
        "id": idOld
      }
    }),
    hostname=str(constant.MQTT_HOST), 
    port=int(constant.MQTT_PORT), 
    client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
  )

oRfid = rfid.rfid(
  remove_callback=rfidRemove,
  insert_callback=rfidInsert,
  change_callback=rfidChange
)

# ===========================================================================
# Rotary encoder
# ===========================================================================

swithRelease = 0
rotateDirection = 'none'

def rotaryRotateCall(direction):
  global rotateDirection
  if args.verbose:
    print('Rotate to ' + direction)
  rotateDirection = direction

def rotarySwitchCall(switchStatus):
  global swithRelease
  if switchStatus=='release':
    swithRelease = 1

oRotary = rotary.rotary(
  switch_callback=rotarySwitchCall,
  rotate_callback=rotaryRotateCall
)

screenStatus = 0

oMqttClient.publish(constant.MQTT_TOPIC_STATE,
  json.dumps({"state": "ready"})
)

# Continually update 
while(True):
  try:
    if screenStatus==0:
      if swithRelease==1:
        screenStatus = 1
        swithRelease = 0
#        oScreen.cls()
        affStart = time.time()
        secondsWait = constant.MENU_WAIT_SECONDS
        waitStep = oScreen.width / (float(secondsWait) * 1000)
        oScreen.draw.rectangle((0, oScreen.height-1, oScreen.width, oScreen.height-1), 0, 1)
        
      else:
        oScreen.pulse()
        oScreen.clock()

    elif screenStatus==1:

      while True:
        affCurrent = time.time() - affStart
        oScreen.draw.rectangle((0, oScreen.height-1, (affCurrent * waitStep) * 1000, oScreen.height-1), 0, 0)
      
#      if swithRelease==1:
        oRotary.triggerDisable()
        oScreen.cls()
        oMenu = menu.menu()
        oMenu.processmenu(oScreen, oRotary, menu_data)
        oRotary.setSwitchCallback(rotarySwitchCall)
        oRotary.setRotateCallback(rotaryRotateCall)
        oRotary.triggerEnable()
        swithRelease = 0
        screenStatus = 0
        oScreen.cls()
        break
      
      oScreen.display()
      
      if affCurrent>secondsWait:
        screenStatus = 0
        oScreen.cls()
        break

    time.sleep(0.001)

    if currentMode == "regular":
      oRfid.loop()

  except KeyboardInterrupt:
    # oRfid.exit()
    oMqttClient.publish(constant.MQTT_TOPIC_ANIMATION_STOP,
      json.dumps({})
    )
    exit()
  except:
    if args.verbose:
      print("Unexpected error:", sys.exc_info()[0])

    raise
    

