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
import hashlib
import random
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
from pathlib import Path
from PIL import ImageFont, ImageDraw, Image
from luma.core.render import canvas

from modules import core
from modules import speak
from modules import network
from modules import menu
from modules import screen
from modules import rotary
from modules import constant
from modules import tools
from modules import rfid
from modules import animator
from modules import mopidy

# ===========================================================================
# Menu definition
# ===========================================================================
menu_data = {
  'title': "General", 'type': constant.MENU_MENU,
  'options':[
    { 'title': "Voix", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Volume", 'type': constant.MENU_COMMAND, 'command': 'setSpeakVolume', 'enable': True },
      ]
    },
    { 'title': "Ecran", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Contraste", 'type': constant.MENU_COMMAND, 'command': 'setScreenContrast', 'enable': True },
      ]
    },
    { 'title': "Animations", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Luminosité", 'type': constant.MENU_COMMAND, 'command': 'setAnimBrightness', 'enable': True },
      ]
    },
    { 'title': "Parametres", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Lumières", 'type': constant.MENU_COMMAND, 'command': 'setLight', 'enable': True },
        { 'title': "Volume", 'type': constant.MENU_COMMAND, 'command': 'setVolume', 'enable': True },
        { 'title': "Informations", 'type': 'viewInfos', 'enable': True}
#        { 'title': "Heure", 'type': constant.MENU_COMMAND, 'command': 'setTime', 'enable': True },
#        { 'title': "Date", 'type': constant.MENU_COMMAND, 'command': 'setDate', 'enable': True },
      ]
    },
  ]
}

gpioMode = GPIO.getmode()
if gpioMode==GPIO.BOARD:
  print('gpioMode BOARD')
else:
  print('gpioMode BCM')
#print('gpioMode ' + str(gpioMode))
#print('gpioMode BOARD ' + str(GPIO.BOARD))
#print('gpioMode BCM ' + str(GPIO.BCM))

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
#oCore.readGeneralConf(sKey, mDefault)
scriptName = Path(__file__).stem
oCore = core.core(scriptName)
pprint.pprint(args.verbose)
oCore.verbose = args.verbose
oCore.setMode(constant.STATE_MODE_STARTING)

# ===========================================================================
# Logging
# ===========================================================================
logging_level: int = oCore.getDebugLevelFromText(oCore.readConf("level", "logging", 'INFO'))
logging_path: str = oCore.readConf("path", "logging", '.')
logging.basicConfig(
  filename=logging_path + '/' + scriptName + '.log', 
  level=int(logging_level),
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S'
)

# ===========================================================================
# Screen
# ===========================================================================
oScreen = screen.screen()
oScreen.cls()
oScreen.contrast(oCore.getScreenContrast())
oScreen.println('Initialisation')
oScreen.println("ip: %s" % network.get_lan_ip())

# ===========================================================================
# MQTT
# ===========================================================================

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
  logging.debug("MQTT Disconnect " + str(reason_code))
  #if args.verbose:
  #  print("MQTT Disconnect " + str(reason_code))

def on_connect(client, userdata, flags, reason_code, properties):
  logging.debug("Connection Success")
  logging.debug("MQTT Subscribe")

  client.subscribe(constant.MQTT_TOPIC_CARTE_ENCODE)
  client.subscribe(constant.MQTT_TOPIC_CARTE_READ)
  client.subscribe(constant.MQTT_TOPIC_MOPIDY_VOL)

  if reason_code != 0:
    logging.critical("Failed to connect, return code %d\n", reason_code)

def on_message(client, userdata, msg):
  global mopidyCurrentTrack

  if args.verbose:
    print(f"MQTT onMessage received `{msg.payload.decode()}` from `{msg.topic}` topic")

  logging.info(f"MQTT onMessage received `{msg.payload.decode()}` from `{msg.topic}` topic")

  if msg.topic == constant.MQTT_TOPIC_CARTE_READ:

    if args.verbose:
      print("Set mode to read")

    logging.info('Set mode to read')
    
    oRfid.setTriggerOff()

    oCore.setMode(constant.STATE_MODE_READ)

    payload = json.loads(msg.payload.decode("utf-8"))

    if args.verbose:
      print('Launch animation')

    logging.info('Launch animation')

    publish.single(
      constant.MQTT_TOPIC_ANIMATION_START,
      json.dumps({
        "name": "blink",
        "brightness": 10,
        "time": 120,
        "parameters": {
          "speed": 0.5,
          "color": "ORANGE"
        }
      }),
      hostname=str(constant.MQTT_HOST),
      port=int(constant.MQTT_PORT),
      client_id=oCore.mqttClientId
    )

    oSpeak.say("Veuillez insérer la carte dans le lecteur...")

    if args.verbose:
      print('Try read card')

    logging.info('Try read card')

    readed = False

    if oRfid.waitInsert(30, oScreen):

      if args.verbose:
        print('Try read...')

      oScreen.picto("cogs")
      id, text = oRfid.readSectors(constant.SECTORS)

      if args.verbose:
        print('id is ' + str(id))
        print('text is ' + str(text))

      if id:
        readed = True

    if readed:
      print('is readed')
      try:
        readPayload = json.loads(text.strip('\x00'))
        readPayload['readed'] = True
        if args.verbose:
          print('payload is decoded')
          pprint.pprint(readPayload)
      except:
        if args.verbose:
          print("Unexpected error:", sys.exc_info()[0])
        readed = False
        pass

    if readed:

      if args.verbose:
        print('Card is readed with ' + text)

      logging.info('Card is readed ' + text)

      oScreen.picto('check-circle');

      msgs = [{'topic': constant.MQTT_TOPIC_CARTE_READED, 'payload': json.dumps(readPayload), "qos": 0, "retain": False},
              {'topic': constant.MQTT_TOPIC_ANIMATION_STOP, 'payload': "{}", "qos": 0, "retain": False}]
      publish.multiple(
        msgs,
        hostname=str(constant.MQTT_HOST),
        port=int(constant.MQTT_PORT),
        client_id=oCore.mqttClientId
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
        client_id=oCore.mqttClientId
      )

      oSpeak.say("La carte est lu !")

    else:

      if args.verbose:
        print('Card is NOT readeded')

      logging.info('Card is NOT readed')

      oScreen.picto('times-circle');

      msgs = [{'topic': constant.MQTT_TOPIC_CARTE_READED, 'payload': '{"readed": False}', "qos": 0, "retain": False},
              {'topic': constant.MQTT_TOPIC_ANIMATION_STOP, 'payload': '{}', "qos": 0, "retain": False}]
      publish.multiple(
        msgs,
        hostname=str(constant.MQTT_HOST),
        port=int(constant.MQTT_PORT),
        client_id=oCore.mqttClientId
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
        client_id=oCore.mqttClientId
      )

      oSpeak.say("La carte n'a pas pu être lue !")

    time.sleep(2)

    oSpeak.say("Veuillez retirer la carte !")

    oRfid.waitRemove(30, oScreen)

    publish.single(
      constant.MQTT_TOPIC_ANIMATION_STOP,
      json.dumps({}),
      hostname=str(constant.MQTT_HOST),
      port=int(constant.MQTT_PORT),
      client_id=oCore.mqttClientId
    )

    oRfid.setTriggerOn()
    oScreen.cls('read');
    oScreen.clock(True);
    oCore.setMode(constant.STATE_MODE_REGULAR)

  elif msg.topic == constant.MQTT_TOPIC_CARTE_ENCODE:

    oRfid.setTriggerOff()

    if args.verbose:
      print("Set mode to encode")

    logging.info('Set mode to encode')

    oCore.setMode(constant.STATE_MODE_ENCODE)

    payload = json.loads(msg.payload.decode("utf-8"))

    if args.verbose:
      print('Launch animation')

    logging.info('Launch animation')

    publish.single(
      constant.MQTT_TOPIC_ANIMATION_START,
      json.dumps({
        "name": "blink",
        "brightness": 10,
        "time": 120,
        "parameters": {
          "speed": 0.5,
          "color": "ORANGE"
        }
      }),
      hostname=str(constant.MQTT_HOST),
      port=int(constant.MQTT_PORT),
      client_id=oCore.mqttClientId
    )

    oSpeak.say("Veuillez insérer la carte dans le lecteur...")

    if args.verbose:
      print('Try write card')

    logging.info('Try write card')

    sUrl = None
    sStyle = constant.STYLE_MUSIC
    sAnimation = constant.ANIMATION_NONE
    bLoop = False
    bShuffle = False
    bOnce = False
    sPicto = ''
    iLimit = 0
    iKeep = 1

    if 'style' in payload:
      if not tools.isEmptyString(payload['style']):
        sStyle = payload['style']
        logging.info('style is not empty')

    if 'url' in payload:
      if not tools.isEmptyString(payload['url']):
        sUrl = payload['url']
        logging.info('url is not empty')

    if 'animation' in payload:
      if not tools.isEmptyString(payload['animation']):
        sAnimation = payload['animation']
        logging.info('animation is not empty')

    if 'loop' in payload:
      if payload['loop'] in [True, False]:
        bLoop = payload['loop']

    if 'shuffle' in payload:
      if payload['shuffle'] in [True, False]:
        bShuffle = payload['shuffle']

    if 'once' in payload:
      if payload['once'] in [True, False]:
        bOnce = payload['once']

    if 'limit' in payload:
      if not tools.isEmpty(payload['limit']):
        iLimit = int(payload['limit'])

    if 'keep' in payload:
      if not tools.isEmpty(payload['keep']):
        iKeep = int(payload['keep'])

    if 'picto' in payload:
      if not tools.isEmptyString(payload['picto']):
        sPicto = payload['picto']

    textEncode = json.dumps({
      "style": sStyle,
      "url": sUrl,
      "animation": sAnimation,
      "shuffle": bShuffle,
      "once": bOnce,
      "loop": bLoop,
      "limit": iLimit,
      "keep": iKeep,
      "picto": sPicto
    }, separators=(',', ':'))

    encoded = False

    if oRfid.waitInsert(30, oScreen):

      if args.verbose:
        print('Try encode with ' + textEncode)

      time.sleep(1)
      oScreen.picto("cogs")
      id, text = oRfid.writeSectors(textEncode, constant.SECTORS)

      if id:
        encoded = True

    if encoded:

      if args.verbose:
        print('Card is encoded with ' + textEncode)

      logging.info('Card is encoded ' + textEncode)

      oScreen.picto('check-circle');

      msgs = [{'topic': constant.MQTT_TOPIC_CARTE_ENCODED, 'payload': '{"encoded": true}', "qos": 0, "retain": False},
              {'topic': constant.MQTT_TOPIC_ANIMATION_STOP, 'payload': "{}", "qos": 0, "retain": False}]
      publish.multiple(
        msgs,
        hostname=str(constant.MQTT_HOST),
        port=int(constant.MQTT_PORT),
        client_id=oCore.mqttClientId
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
        client_id=oCore.mqttClientId
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
        client_id=oCore.mqttClientId
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
        client_id=oCore.mqttClientId
      )

      oSpeak.say("La carte n'a pas pu être encodée !")

    time.sleep(2)

    oSpeak.say("Veuillez retirer la carte !")

    oRfid.waitRemove(30, oScreen)

    publish.single(
      constant.MQTT_TOPIC_ANIMATION_STOP,
      json.dumps({}),
      hostname=str(constant.MQTT_HOST),
      port=int(constant.MQTT_PORT),
      client_id=oCore.mqttClientId
    )
    
    oRfid.setTriggerOn()

    oScreen.cls('write');
    oScreen.clock(True);
    oCore.setMode(constant.STATE_MODE_REGULAR)

  elif msg.topic == constant.MQTT_TOPIC_MOPIDY_VOL:
    payload = msg.payload.decode('utf-8')
    mopidyCurrentTrack['volume'] = int(payload)

# connect to mqtt server
oScreen.println("Connect to MQTT on " + constant.MQTT_HOST + ':' + str(constant.MQTT_PORT))
oMqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, oCore.mqttClientId)
oMqttClient.on_connect = on_connect
oMqttClient.on_message = on_message
oMqttClient.on_disconnect = on_disconnect
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
  client_id=oCore.mqttClientId
)

# ===========================================================================
# Mopidy
# ===========================================================================
oScreen.println("Init mopidy")

def mopidyStatusChange(newStatus, oldStatus):

  if args.verbose:
    print("Mopidy state change " + oldStatus + " to " + newStatus)

  logging.info("Mopidy state change " + oldStatus + " to " + newStatus)

  if oCore.getMode() == constant.STATE_MODE_STARTING:
    if args.verbose:
      print("Mopidy is in starting mode bypass change status")

    return True

  if newStatus=='playing':

    mopidyCurrentTrack = oMopidy.getCurrentTrack()
    volume = oCore.getSpecificVolume(mopidyCurrentTrack['id'])
    oMopidy.volume_set(volume)

    oCore.setMode(constant.STATE_MODE_PLAY)
    #oScreen.play(currentTrack, True)

  if newStatus in ['paused', 'stop', 'stopped']:
    oMopidy.stop()
    oMopidy.tracklist_clear()
    oCore.setMode(constant.STATE_MODE_REGULAR)
    oMqttClient.publish(constant.MQTT_TOPIC_ANIMATION_STOP,
      json.dumps({})
    )
    oScreen.clock(True)
    
oMopidy = mopidy.mopidy(
  core = oCore,
  logging = logging,
  change_callback=mopidyStatusChange
)
oMopidy.verbose = args.verbose
oMopidy.stop()
oMopidy.tracklist_clear()
mopidyCurrentTrack = oMopidy.getCurrentTrack()

# ===========================================================================
# Speak
# ===========================================================================
oScreen.println("Init speak")
oSpeak = speak.speak(
  core = oCore,
  logging = logging,
  mopidy = oMopidy
)
oSpeak.verbose = args.verbose
oSpeak.logging = logging

# ===========================================================================
# Rfid
# ===========================================================================
def rfidChange(id, jsonDatas, idOld, jsonDatasOld):
  if args.verbose:
    print('change to ' + id + ' : ' + json.dumps(jsonDatas))

  publish.single(
    constant.MQTT_TOPIC_RFID,
    json.dumps({
      "action": "change",
      "datas": jsonDatas,
      "id": id,
      "old": {
        "datas": jsonDatasOld,
        "id": idOld
      }
    }),
    hostname=str(constant.MQTT_HOST),
    port=int(constant.MQTT_PORT),
    client_id=oCore.mqttClientId
  )

def rfidRemove(id, jsonDatas):
  if args.verbose:
    print('Remove to ' + id + ' : ' + json.dumps(jsonDatas))

  logging.info('Remove to ' + id + ' : ' + json.dumps(jsonDatas))

  publish.single(
    constant.MQTT_TOPIC_RFID,
    json.dumps({
      "action": "remove",
      "datas": jsonDatas,
      "id": id
    }),
    hostname=str(constant.MQTT_HOST),
    port=int(constant.MQTT_PORT),
    client_id=oCore.mqttClientId
  )

  if args.verbose:
    print("Stop play")

  oMopidy.stop()

def rfidInsert(id, jsonDatas):
  global mopidyCurrentTrack

  if args.verbose:
    print('Insert to ' + id + ' : ' + json.dumps(jsonDatas))

  publish.single(
    constant.MQTT_TOPIC_RFID,
    json.dumps({
      "action": "insert",
      "datas": jsonDatas,
      "id": id
    }),
    hostname=str(constant.MQTT_HOST),
    port=int(constant.MQTT_PORT),
    client_id=oCore.mqttClientId
  )
  if oCore.getMode()==constant.STATE_MODE_REGULAR:
    try:
      
      oCore.setMode(constant.STATE_MODE_WAITPLAY)
      oScreen.wait(True, 'Préparation de la liste de lecture')
      time.sleep(0.5)

      sUrl = 'unknow'
      sStyle = constant.STYLE_MUSIC
      sAnimation = constant.ANIMATION_NONE
      bLoop = False
      bShuffle = False
      bOnce = False
      iLimit = 0
      iKeep = 1

      if 'url' in jsonDatas:
        if not tools.isEmptyString(jsonDatas['url']):
          sUrl = jsonDatas['url']

      sMessage = "lauch url " + sUrl

      if 'style' in jsonDatas:
        if jsonDatas['style'] in [constant.STYLE_LOVE, constant.STYLE_ZEN, constant.STYLE_NATURE, constant.STYLE_MUSIC, constant.STYLE_RELAX]:
          sStyle = jsonDatas['style']
          sMessage = sMessage + ' whith style ' + sStyle
      else:
        jsonDatas['style'] = sStyle

      if 'picto' in jsonDatas:
        if not tools.isEmptyString(jsonDatas['picto']):
          fileName = self.core.getRootPath() + "icons/mode-" + jsonDatas['picto'] + ".png"
          if os.path.isfile(fileName):
            jsonDatas['style'] = jsonDatas['picto']
            sStyle = jsonDatas['style']
            sMessage = sMessage + ' override style with ' + sStyle

      if 'loop' in jsonDatas:
        if jsonDatas['loop'] in [True, False]:
          bLoop = jsonDatas['loop']
          sMessage = sMessage + ' use loop'
      else:
        jsonDatas['loop'] = bLoop

      if 'shuffle' in jsonDatas:
        if jsonDatas['shuffle'] in [True, False]:
          bShuffle = jsonDatas['shuffle']
          sMessage = sMessage + ' and shuffle list'
      else:
        jsonDatas['shuffle'] = bShuffle

      if 'once' in jsonDatas:
        if jsonDatas['once'] in [True, False]:
          bOnce = jsonDatas['once']
          sMessage = sMessage + ' and play once'
      else:
        jsonDatas['once'] = bOnce

      if 'limit' in jsonDatas:
        if not tools.isEmpty(jsonDatas['limit']):
          iLimit = jsonDatas['limit']
          sMessage = sMessage + ' and limit ' + str(iLimit)
      else:
        jsonDatas['limit'] = iLimit

      if 'keep' in jsonDatas:
        if not tools.isEmpty(jsonDatas['keep']):
          iKeep = jsonDatas['keep']
          sMessage = sMessage + ' and keep ' + str(iKeep)
      else:
        jsonDatas['keep'] = iKeep

      if 'animation' in jsonDatas:
        if jsonDatas['animation'] in [constant.ANIMATION_NONE, constant.ANIMATION_SPARKLEPULSE]:
          sAnimation = jsonDatas['animation']
          sMessage = sMessage + ' play animation ' + sAnimation
      else:
        jsonDatas['animation'] = sAnimation

      if not tools.isEmptyString(jsonDatas['url']):
        sUrl = jsonDatas['url']

        if args.verbose:
          print(sMessage)

        logging.info(sMessage)

        oCore.setMode(constant.STATE_MODE_WAITPLAY)
        oScreen.wait(True, 'Lancement de la lecture')
        time.sleep(0.5)

        h = hashlib.new('sha1')
        h.update(sUrl.encode())
        jsonDatas['id'] = h.hexdigest()

        volume = oCore.getSpecificVolume(jsonDatas['id'])
        oMopidy.volume_set(volume)

        mopidyCurrentTrack = {**mopidyCurrentTrack, **jsonDatas}

        logging.info("Create playlist")
        oMopidy.create_playlist(
          sUrl,
          bOnce,
          bShuffle,
          bLoop,
          iKeep
        )
        logging.info("Create playlist success")

        animBrightness = oCore.getAnimBrightness()

        if oCore.getLight()==1:
          if sAnimation == constant.ANIMATION_SPARKLEPULSE:
            publish.single(
              constant.MQTT_TOPIC_ANIMATION_START,
              json.dumps({
                "name": "sparklepulse",
                "brightness": animBrightness,
                "time": 86400,
                "parameters": {
                  "speed": 0.05,
                  "color": "BLUE",
                  "num_sparkles": 10,
                  "breath": 0.5,
                  "period": 2,
                  "max_intensity": 1,
                  "min_intensity": 0.2
                }
              }),
              hostname=str(constant.MQTT_HOST),
              port=int(constant.MQTT_PORT),
              client_id=oCore.mqttClientId
            )

      else:
        oCore.setMode(constant.STATE_MODE_REGULAR)
        if args.verbose:
          print("Not lauch music " + sStyle + ", " + sMode + " because we have no url")
        logging.info("Not lauch music " + sStyle + ", " + sMode + " because we have no url")

    except:
      oCore.setMode(constant.STATE_MODE_REGULAR)
      if args.verbose:
        print("Json decode datas unexpected error:", sys.exc_info()[0])
      logging.error("Json decode datas unexpected error:", sys.exc_info()[0])
      pass

def rfidPresence(status):
  if args.verbose:
    print('RFID card is ' + status)

oScreen.println("Init lecteur RFID")
oRfid = rfid.rfid(
  remove_callback=rfidRemove,
  insert_callback=rfidInsert,
  change_callback=rfidChange,
  presence_callback=rfidPresence,
  sectors=constant.SECTORS
)

# ===========================================================================
# Rotary encoder
# ===========================================================================

swithRelease = 0
rotateDirection = 'none'

def rotaryRotateCall(direction):
  global rotateDirection, mopidyCurrentTrack
  if args.verbose:
    print('Rotate to ' + direction)
  rotateDirection = direction

  if oCore.getMode()==constant.STATE_MODE_PLAY:
    if rotateDirection=='left':
      volume = oCore.getSpecificVolume(mopidyCurrentTrack['id']) + 1
      oCore.setSpecificVolume(mopidyCurrentTrack['id'], volume)
      oMopidy.volume_set(volume)
      mopidyCurrentTrack['volume'] = int(volume)
      oScreen.play(mopidyCurrentTrack, True)
      if args.verbose:
        print('Set specific volume ' + str(volume) + ' for ' + str(mopidyCurrentTrack['id']))
    else:
      volume = oCore.getSpecificVolume(mopidyCurrentTrack['id']) - 1
      oCore.setSpecificVolume(mopidyCurrentTrack['id'], volume)
      oMopidy.volume_set(volume)
      mopidyCurrentTrack['volume'] = int(volume)
      oScreen.play(mopidyCurrentTrack, True)
      if args.verbose:
        print('Set specific volume ' + str(volume) + ' for ' + str(mopidyCurrentTrack['id']))

def rotarySwitchCall(switchStatus):
  global swithRelease
  if switchStatus=='release':
    swithRelease = 1

oScreen.println("Init bouton rotatif")
oRotary = rotary.rotary(
  switch_callback=rotarySwitchCall,
  rotate_callback=rotaryRotateCall
)

oMqttClient.publish(constant.MQTT_TOPIC_STATE,
  json.dumps({"state": "ready"})
)

oScreen.println("Initialisation terminée!")
oSpeak.say("Initialisation terminée!")
time.sleep(10)

oCore.setMode(constant.STATE_MODE_REGULAR)

oScreen.clock(True);

# Continually update
while(True):
  try:
    if oCore.getMode()==constant.STATE_MODE_REGULAR:
      if swithRelease==1:
        oCore.setMode(constant.STATE_MODE_MENU)
        swithRelease = 0
        affStart = time.time()
        secondsWait = constant.MENU_WAIT_SECONDS
        waitStep = oScreen.width / (float(secondsWait) * 1000)
        oScreen.draw.rectangle((0, oScreen.height-1, oScreen.width, oScreen.height-1), 0, 1)

      else:
        oScreen.clock()

    if oCore.getMode()==constant.STATE_MODE_MENU:
      while True:
        affCurrent = time.time() - affStart
        oScreen.draw.rectangle((0, oScreen.height-1, (affCurrent * waitStep) * 1000, oScreen.height-1), 0, 0)

        oRotary.triggerDisable()
        oScreen.cls('menu')
        oMenu = menu.menu(
          core = oCore
        )
        oMenu.processmenu(oScreen, oRotary, menu_data)
        oRotary.setSwitchCallback(rotarySwitchCall)
        oRotary.setRotateCallback(rotaryRotateCall)
        oRotary.triggerEnable()
        swithRelease = 0
        oCore.setMode(constant.STATE_MODE_REGULAR)
        oScreen.cls('menu out')
        break

      oScreen.display()

      if affCurrent>secondsWait:
        oCore.setMode(constant.STATE_MODE_REGULAR)
        oScreen.cls('menu wait')
        break

    if oCore.getMode()==constant.STATE_MODE_WAITPLAY:
      if oScreen.waitPlay(oCore):
        oCore.setMode(constant.STATE_MODE_REGULAR)
        oMopidy.stop()
        oScreen.clock(True)

    if oCore.getMode()==constant.STATE_MODE_PLAY:
      oScreen.play(mopidyCurrentTrack)

    time.sleep(0.5)

  except KeyboardInterrupt:
    oMqttClient.publish(constant.MQTT_TOPIC_ANIMATION_STOP,
      json.dumps({})
    )
    exit()
  except:
    if args.verbose:
      print("Unexpected error:", sys.exc_info()[0])

    raise


