import sys
import os
import re
import signal
import argparse
import time
import configparser
import pprint
import datetime
import logging
import logging.handlers
import RPi.GPIO as GPIO
import socketio
import paho.mqtt.client as mqtt
import random
import json
import threading
import asyncio
from pathlib import Path
from aiohttp import web
from modules import constant
from modules import core

# ===========================================================================
# Param
# ===========================================================================
parser = argparse.ArgumentParser(description="Morphe manager service")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
args = parser.parse_args()

# ===========================================================================
# Import config
# ===========================================================================
oCore = core.core()
scriptName = Path(__file__).stem

# ===========================================================================
# Logging
# ===========================================================================
logging_level: int = oCore.readConf("level", "logging", 20)
logging_path: str = oCore.readConf("path", "logging", '.')
logging.basicConfig(filename=logging_path + '/' + scriptName + '.log', level=int(logging_level))

#sio = socketio.AsyncServer(logger=True, engineio_logger=True)
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

async def index(request):
  """Serve the client-side application."""
  with open('server/index.html') as f:
    return web.Response(text=f.read(), content_type='text/html')

@sio.event
def connect(sid, environ):
  print("connect ", sid)

@sio.event
def disconnect(sid):
  print('disconnect ', sid)

### CARDS
@sio.event
async def encode_card(sid, url, style):
  if url=='' or url==None:
    await sio.emit('encode_ack', {'ack': False, 'title': 'Erreur', 'message': "L'url ne doit pas etre vide"})
    return True

  if style=='' or style==None:
    await sio.emit('encode_ack', {'ack': False, 'title': 'Erreur', 'message': "Le style doit etre defini"})
    return True

  oMqttClient.publish(constant.MQTT_TOPIC_CARTE_ENCODE,
    json.dumps({
      "url": url,
      "style": style
    })
  )
  await sio.emit('encode_ack', {'ack': True})  
  time.sleep(0.50)

async def encoded_card(ack, title = "", message = ""):
  await sio.emit('encoded_ack', {'ack': ack, 'title': title, 'message': message})
  time.sleep(0.50)

@sio.event
async def set_volume(sid, data):
  oCore = core.core()
  oCore.setVolume(data)
  await sio.emit('update_volume', {'volume': str(data)})

app.router.add_static('/static', 'server/static')
app.router.add_get('/', index)

# ===========================================================================
# MQTT
# ===========================================================================
def on_connect(client, userdata, flags, reason_code, properties):
  if args.verbose:
    print("MQTT Connection Success")

  client.subscribe(constant.MQTT_TOPIC_CARTE_ENCODE)
  client.subscribe(constant.MQTT_TOPIC_CARTE_ENCODED)

  if reason_code == 0:
    logging.info("MQTT Connection Success")
  else:
    logging.critical("Failed to connect, return code %d\n", reason_code)

def on_message(client, userdata, msg):

  if args.verbose:
    print("MQTT onMessage")
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
  
  logging.info(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

  if msg.topic == constant.MQTT_TOPIC_CARTE_ENCODED:

    payload = msg.payload.decode("utf-8")
    logging.info("Recevied encoded_ack")
    asyncio.run(encoded_card(ack=True))
    time.sleep(0.5)
    
oMqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, f"mqtt-{scriptName}-{random.randint(0, 1000)}")
oMqttClient.on_message = on_message
oMqttClient.on_connect = on_connect
oMqttClient.connect(str(constant.MQTT_HOST), int(constant.MQTT_PORT))
oMqttClient.loop_start();
print("MQTT Subscribe")
if __name__ == '__main__':
    web.run_app(app, port=80)
    
