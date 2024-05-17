import sys
import os
import re
import signal
import logging
import argparse
import time
import configparser
import requests
import json
import pprint
import datetime
import hashlib

from modules import core
from modules import tools
from modules import constant

# ===========================================================================
# mopidy Class
# ===========================================================================

class mopidy():

  def __init__(self):
    self.core = core.core()
    self.verbose = False
    self.logging = False
    self.volume = constant.MOPIDY_VOLUME
    self.volume_set(self.volume)
    self.tracklist_off()

  #toggle play pause
  def play_pause(self):
    #get current playback state first
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.get_state"})

    logging.info('MOPIDY play_pause ' + r.text)
  
    if r.text.find('playing') == -1:
      #not playing, go to play
      self.play()
    else:
      #playing, go to pause
      self.pause()

  #go to play
  def play(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"})
    time.sleep(0.1)
    logging.info('MOPIDY play > ' + r.text)

  #go to pause
  def pause(self):      
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.pause"})
    time.sleep(0.1)
    logging.info('MOPIDY pause > ' + r.text)

  #play next track       
  def next(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.next"})
    time.sleep(0.1)
    logging.info('MOPIDY next > ' + r.text)

  #stop playback, clear tracklist
  def stop(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.stop"})
    time.sleep(0.1)
    logging.info('MOPIDY stop > ' + r.text)

  #clear tracklist
  def tracklist_clear(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.clear"})
    time.sleep(0.1)
    logging.info('MOPIDY tracklist_clear > ' + r.text)

  #increase volume but not higher than 100
  def volume_up(self):
    self.volume = self.volume + 1
    self.volume_set(volume)

  #decrease volume but not lower than 0
  def volume_down(self):
    self.volume = self.volume - 1
    self.volume_set(volume)
    
  def volume_set(self, volume):
    volume = int(volume)
    if volume < 0:
      volume = 0
    elif volume > 100:
      volume = 100

    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.mixer.set_volume", "params": {"volume": volume}})
    time.sleep(0.1)
    logging.info('MOPIDY volume_set ' + str(volume) + ' > ' + r.text)

  def new_playlist(self, uri):

    URITypePlaylist = uri.find('playlist') != -1

    #Pause playback first
    self.pause()

    #Clear existing tracklist
    self.tracklist_clear()

    #Add URI to tracklist
    r = requests.post(constant.MOPIDY_URL, json={"method": "core.tracklist.add", "jsonrpc": "2.0", "params": {"uris": [uri]}, "id": 1})
    time.sleep(0.5)
    logging.info('MOPIDY new_playlist ' + uri + ' > ' + r.text)

    #If the URI is a playlist, set shuffle ON, else set shuffle OFF
    if URITypePlaylist:
      r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_random", "params": {"value": True}})
      time.sleep(0.1)
      logging.info('MOPIDY new_playlist set random true > ' + r.text)
    else:
      r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_random", "params": {"value": False}})
      time.sleep(0.1)
      logging.info('MOPIDY new_playlist set random false > ' + r.text)

    #Start playing tracklist
    self.play()

  #set consume for tracklist repeat
  def tracklist_repeat(self, value = False):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": value}})
    time.sleep(0.1)
    logging.info('MOPIDY set_repeat > ' + r.text)

  #set consume for tracklist single
  def tracklist_single(self, value = False):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_single", "params": {"value": value}})
    time.sleep(0.1)
    logging.info('MOPIDY set_single > ' + r.text)

  #set consume for tracklist consume
  def tracklist_consume(self, value = False):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_consume", "params": {"value": value}})
    time.sleep(0.1)
    logging.info('MOPIDY set_consume > ' + r.text)

  #set consume for tracklist off
  def tracklist_off(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_consume", "params": {"value": False}})
    time.sleep(0.1)
    logging.info('MOPIDY tracklist_off > ' + r.text)

  def get_playing_details(self):
    result = {
      'length': 0,
      'position': 0,
      'artist': '',
      'album': '',
      'name': 0
    }
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.get_current_track"})
    if r.status_code==200:
      try:
        jsonDatas = r.json()['result']
    
        if not tools.isEmpty(jsonDatas):

          if not tools.isEmpty(jsonDatas['uri']):
            result['url'] = jsonDatas['uri']
            
          if not tools.isEmpty(jsonDatas['length']):
            result['length'] = jsonDatas['length']
          
          if not tools.isEmptyString(jsonDatas['name']):
            result['name'] = jsonDatas['name']

          if 'album' in jsonDatas:
            if not tools.isEmptyString(jsonDatas['album']['name']):
              result['album'] = jsonDatas['album']['name']

          if 'artists' in jsonDatas:
            if not tools.isEmptyString(jsonDatas['artists'][0]['name']):
              result['artist'] = jsonDatas['artists'][0]['name']

      except:
        logging.error("get_playing_details unexpected error:", sys.exc_info()[0])
        raise

    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.get_time_position"})
    if r.status_code==200:
      try:
        jsonDatas = r.json()['result']
        
        if not tools.isEmpty(jsonDatas):
          result['position'] = jsonDatas

      except:

        logging.error("get_playing_details unexpected error:", sys.exc_info()[0])
        raise

    logging.info('MOPIDY get_playing_details > ' + r.text)
    
    return result