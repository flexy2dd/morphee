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
import paho.mqtt.publish as publish

from modules import core
from modules import tools
from modules import constant

# ===========================================================================
# mopidy Class
# ===========================================================================

class mopidy():

  def __init__(self, **params):

    self.core = None
    self.logging = False
    self.verbose = False
    self.volume = constant.MOPIDY_VOLUME
    self.volume_set(self.volume)
    self.tracklist_off()

    if 'core' in params:
      self.core = params['core']

    if 'logging' in params:
      self.logging = params['logging']
    else:
      logging_level: int = self.core.getDebugLevelFromText(self.core.readConf("level", "logging", 'INFO'))
      logging.basicConfig(level=int(logging_level))

    if 'change_callback' in params:
      self.changeCallback = params['change_callback']

    if 'update_callback' in params:
      self.updateCallback = params['update_callback']

    self.timerStatus = tools.PeriodicTimer(1, self.getPlayingStatus)
    self.timerStatus.start()

    self.timerDetails = tools.PeriodicTimer(2, self.getPlayingDetails)
    self.timerDetails.start()

    self.currentTrack = mopidyCurrentTrack = {
      'mode': constant.MODE_ONCE,
      'style': constant.STYLE_MUSIC,
      'url': '',
      'length': 0,
      'position': 0,
      'artist': '',
      'album': '',
      'name': '',
      'id': '',
      'volume': 0
    }
    self.currentStatus = ''

  def getCurrentTrack(self):
    return self.currentTrack

  def getPlayingDetails(self):

    self.logging.debug("Mopidy check playing details")

    if self.core.getMode() == constant.STATE_MODE_PLAY:
      result = self.get_playing_details()

      self.currentTrack = {**self.currentTrack, **result}

      publish.single(
        constant.MQTT_TOPIC_MOPIDY_TRKINFOS,
        json.dumps(self.currentTrack),
        hostname=str(constant.MQTT_HOST),
        port=int(constant.MQTT_PORT),
        client_id=self.core.mqttClientId
      )

      if not self.updateCallback is None:
        self.logging.debug("Mopidy call update callback")
        self.updateCallback(self.currentTrack)

    return True

  def getCurrentStatus(self):
    return self.currentStatus

  def getPlayingStatus(self):

    if self.core.getMode() == constant.STATE_MODE_STARTING:
      return True

    self.logging.debug("Mopidy check playing status")

    #'playing', 'paused', 'stop', 'stopped'
    result = self.playback_get_state()
    if self.currentStatus != result:

      logging.info("Mopidy state change " + self.currentStatus + " to " + result)

      oldStatus = self.currentStatus
      self.currentStatus = result

      if self.currentStatus in ['playing'] and tools.isEmpty(self.currentTrack['id']):
        currentTrack = self.getCurrentTrack()
        sUrl = currentTrack['url']
      
        h = hashlib.new('sha1')
        h.update(sUrl.encode())
        self.currentTrack['id'] = h.hexdigest()

      if self.currentStatus in ['paused', 'stop', 'stopped']:
        self.currentTrack['id'] = ''

      #self.triggerChange(self.currentStatus)
      if not self.changeCallback is None:
        self.logging.debug("Mopidy call change callback")
        self.changeCallback(self.currentStatus, oldStatus)

    return True

  #toggle play pause
  def play_pause(self):
    #get current playback state first
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.get_state"})

    logging.debug('MOPIDY play_pause ' + r.text)

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
    logging.debug('MOPIDY play > ' + r.text)

  #go to pause
  def pause(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.pause"})
    time.sleep(0.1)
    logging.debug('MOPIDY pause > ' + r.text)

  #play next track
  def next(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.next"})
    time.sleep(0.1)
    logging.debug('MOPIDY next > ' + r.text)

  #stop playback, clear tracklist
  def stop(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.stop"})
    time.sleep(0.1)
    logging.debug('MOPIDY stop > ' + r.text)

  #clear tracklist
  def tracklist_clear(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.clear"})
    time.sleep(0.1)
    logging.debug('MOPIDY tracklist_clear > ' + r.text)

  #set consume for tracklist repeat
  def tracklist_repeat(self, value = False):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": value}})
    time.sleep(0.1)
    logging.debug('MOPIDY set_repeat > ' + r.text)

  #set consume for tracklist single
  def tracklist_single(self, value = False):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_single", "params": {"value": value}})
    time.sleep(0.1)
    logging.debug('MOPIDY set_single > ' + r.text)

  #set consume for tracklist consume
  def tracklist_consume(self, value = False):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_consume", "params": {"value": value}})
    time.sleep(0.1)
    logging.debug('MOPIDY set_consume > ' + r.text)

  #set consume for tracklist off
  def tracklist_off(self):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_consume", "params": {"value": False}})
    time.sleep(0.1)
    logging.debug('MOPIDY tracklist_off > ' + r.text)

  #set shuffle tracklist
  def tracklist_shuffle(self, start  = None, end = None):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.shuffle", "params": {"start": start, "end": end}})
    print(r.text)
    time.sleep(0.1)
    logging.debug('MOPIDY tracklist_shuffle > ' + r.text)

  #set remove for tracklist
  # Parameters: criteria (dict[Literal['tlid', 'uri', 'name', 'genre', 'comment', 'musicbrainz_id'], Iterable[str | int]]) – one or more rules to match by
  def tracklist_remove(self, criteria = []):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.remove", "params": {"criteria": criteria}})
    time.sleep(0.1)
    logging.debug('MOPIDY tracklist_remove > ' + r.text)

  #set move for tracklist
  # Parameters:
  # start (int) – position of first track to move
  # end (int) – position after last track to move
  # to_position (int) – new position for the tracks
  def tracklist_move(self, start, end, to_position):
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.move", "params": {"start": start, "end": end, "to_position": to_position}})
    time.sleep(0.1)
    logging.debug('MOPIDY tracklist_move > ' + r.text)

  #get tracklist length
  def tracklist_length(self):
    result = 0
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.get_length"})
    if r.status_code==200:
      try:
        jsonDatas = r.json()['result']

        if not tools.isEmpty(jsonDatas):
          result = jsonDatas

      except:

        logging.error("get_length unexpected error:", sys.exc_info()[0])
        raise

    time.sleep(0.1)
    logging.debug('MOPIDY tracklist_legth > ' + r.text)

    return result

  #get tracklist slice
  # Returns a slice of the tracklist, limited by the given start and end positions.
  # Parameters:
  # start (int) – position of first track to include in slice
  # end (int) – position after last track to include in slice
  def tracklist_slice(self, start, end):
    result = []
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.slice", "params": {"start": start, "end": end}})
    time.sleep(0.1)
    if r.status_code==200:
      try:
        result = r.json()['result']

      except:
        logging.error("tracklist_slice unexpected error:", sys.exc_info()[0])
        raise

    logging.debug('MOPIDY tracklist_slice > ' + r.text)

    return result


  #get playback state
  def playback_get_state(self):
    result = 'stopped'
    r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.get_state"})
    if r.status_code==200:
      try:
        jsonDatas = r.json()['result']

        if not tools.isEmpty(jsonDatas):
          result = jsonDatas

      except:

        logging.error("get_state unexpected error:", sys.exc_info()[0])
        raise

    logging.debug('MOPIDY playback_get_state > ' + r.text)

    return result

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
    logging.debug('MOPIDY volume_set ' + str(volume) + ' > ' + r.text)

  def create_playlist(self, uri, isOnce = True, isShuffle = False, isLoop = False, keep = 1):
    isPlaylist = uri.find('playlist') != -1
    isAlbum = uri.find('album') != -1

    #Pause playback first
    self.pause()

    #Clear existing tracklist
    self.tracklist_clear()

    r = requests.post(constant.MOPIDY_URL, json={"method": "core.tracklist.add", "jsonrpc": "2.0", "params": {"uris": [uri]}, "id": 1})
    time.sleep(0.1)

    length = self.tracklist_length()

    if isLoop:
      self.tracklist_repeat()

    if isShuffle:
      self.tracklist_shuffle()

    if isOnce:
      if length > keep:
        tracklistSlice = self.tracklist_slice(keep, length)
        if len(tracklistSlice)>0:
          trackList = []
          for track in tracklistSlice:
            trackList.append(int(track['tlid']))

          self.tracklist_remove({'tlid': trackList})

    logging.debug('MOPIDY create_playlist ' + uri + ' > ' + r.text)

    self.play()

  def new_playlist(self, uri):

    URITypePlaylist = uri.find('playlist') != -1

    #Pause playback first
    self.pause()

    #Clear existing tracklist
    self.tracklist_clear()

    #Add URI to tracklist
    r = requests.post(constant.MOPIDY_URL, json={"method": "core.tracklist.add", "jsonrpc": "2.0", "params": {"uris": [uri]}, "id": 1})
    time.sleep(0.5)
    logging.debug('MOPIDY new_playlist ' + uri + ' > ' + r.text)

    #If the URI is a playlist, set shuffle ON, else set shuffle OFF
    if URITypePlaylist:
      r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_random", "params": {"value": True}})
      time.sleep(0.1)
      logging.debug('MOPIDY new_playlist set random true > ' + r.text)
    else:
      r = requests.post(constant.MOPIDY_URL, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_random", "params": {"value": False}})
      time.sleep(0.1)
      logging.debug('MOPIDY new_playlist set random false > ' + r.text)

    #Start playing tracklist
    self.play()

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

    logging.debug('MOPIDY get_playing_details > ' + r.text)

    return result
