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
import paho.mqtt.publish as publish
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
logging_level: int = oCore.getDebugLevelFromText(oCore.readConf("level", "logging", 'INFO'))
logging_path: str = oCore.readConf("path", "logging", '.')
logging.basicConfig(
  filename=logging_path + '/' + scriptName + '.log', 
  level=int(logging_level),
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S'
)

#sio = socketio.AsyncServer(logger=True, engineio_logger=True)
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

async def index(request):
  """Serve the client-side application."""
  with open('server/index.html') as f:
    return web.Response(text=f.read(), content_type='text/html')

async def old(request):
  """Serve the client-side application."""
  with open('server/index-old.html') as f:
    return web.Response(text=f.read(), content_type='text/html')

@sio.event
def connect(sid, environ):
  print("connect ", sid)

@sio.event
def disconnect(sid):
  print('disconnect ', sid)

### CARDS
@sio.event
async def encode_card(sid, jDatas):

  pprint.pprint(jDatas)
  pprint.pprint(jDatas['url'])

  if jDatas['url']=='' or jDatas==None:
    await sio.emit('encode_ack', {'ack': False, 'title': 'Erreur', 'message': "L'url ne doit pas etre vide"})
    return True

  if jDatas['style']=='' or jDatas==None:
    await sio.emit('encode_ack', {'ack': False, 'title': 'Erreur', 'message': "Le style doit etre defini"})
    return True

  if jDatas['animation']=='' or jDatas==None:
    await sio.emit('encode_ack', {'ack': False, 'title': 'Erreur', 'message': "L'animation doit etre definie"})
    return True

  if jDatas['once']=='' or jDatas==None:
    await sio.emit('encode_ack', {'ack': False, 'title': 'Erreur', 'message': "Le mode unique doit etre defini"})
    return True

  if jDatas['shuffle']=='' or jDatas==None:
    await sio.emit('encode_ack', {'ack': False, 'title': 'Erreur', 'message': "Le mode aléatoire etre defini"})
    return True

  if jDatas['loop']=='' or jDatas==None:
    await sio.emit('encode_ack', {'ack': False, 'title': 'Erreur', 'message': "Le mode boucle doit etre defini"})
    return True

  if jDatas['limit']=='' or jDatas==None:
    await sio.emit('encode_ack', {'ack': False, 'title': 'Erreur', 'message': "La limite doit etre defini"})
    return True

  publish.single(
    constant.MQTT_TOPIC_CARTE_ENCODE,
    json.dumps(jDatas),
    hostname=str(constant.MQTT_HOST),
    port=int(constant.MQTT_PORT),
    client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
  )

  await sio.emit('encode_ack', {'ack': True})
  time.sleep(0.50)

async def encoded_card(ack, title = "", message = ""):
  await sio.emit('encoded_ack', {'ack': ack, 'title': title, 'message': message})
  time.sleep(0.50)

@sio.event
async def read_card(sid):
  publish.single(
    constant.MQTT_TOPIC_CARTE_READ,
    json.dumps({}),
    hostname=str(constant.MQTT_HOST),
    port=int(constant.MQTT_PORT),
    client_id=f"mqtt-{scriptName}-{random.randint(0, 1000)}"
  )
  time.sleep(0.50)

app.router.add_static('/css', 'server/css')
app.router.add_static('/scss', 'server/scss')
app.router.add_static('/images', 'server/images')
app.router.add_static('/custom', 'server/custom')
app.router.add_static('/assets', 'server/assets')
app.router.add_static('/js', 'server/js')
app.router.add_get('/old', old)
app.router.add_get('/index.html', index)
app.router.add_get('/', index)

print("MQTT Subscribe")
if __name__ == '__main__':
    web.run_app(app, port=80)

