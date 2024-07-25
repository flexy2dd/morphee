import sys
import getopt
import argparse
import os
import re
import random
import time
import configparser
import pprint
import datetime
import board
import neopixel
import logging
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import json
import paho.mqtt.client as mqtt
import threading
from pathlib import Path

from modules import core
from modules import constant

from adafruit_led_animation.animation.volume            import Volume
from adafruit_led_animation.animation.sparklepulse      import SparklePulse
from adafruit_led_animation.animation.sparkle           import Sparkle
from adafruit_led_animation.animation.rainbowsparkle    import RainbowSparkle
from adafruit_led_animation.animation.solid             import Solid
from adafruit_led_animation.animation.chase             import Chase
from adafruit_led_animation.animation.comet             import Comet
from adafruit_led_animation.animation.colorcycle        import ColorCycle
from adafruit_led_animation.animation.blink             import Blink
from adafruit_led_animation.animation.customcolorchase  import CustomColorChase
from adafruit_led_animation.animation.grid_rain         import Rain
from adafruit_led_animation.animation.multicolor_comet  import MulticolorComet
from adafruit_led_animation.animation.pulse             import Pulse
from adafruit_led_animation.animation.rainbow           import Rainbow
from adafruit_led_animation.animation.rainbowchase      import RainbowChase
from adafruit_led_animation.animation.rainbowcomet      import RainbowComet
from adafruit_led_animation.color import WHITE, RED, YELLOW, ORANGE, GREEN, TEAL, CYAN, BLUE, PURPLE, MAGENTA, BLACK, GOLD, PINK, AQUA, JADE, AMBER, OLD_LACE, RGBW_WHITE_RGB, RGBW_WHITE_W, RGBW_WHITE_RGBW, RAINBOW

# ===========================================================================
# Param
# ===========================================================================
parser = argparse.ArgumentParser(description="Morphe lights service")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
args = parser.parse_args()

# ===========================================================================
# Import config
# ===========================================================================
scriptName = Path(__file__).stem
oCore = core.core(scriptName)

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
# global
# ===========================================================================
animation = 'none'
animationParams = []
animationTime = 86400
animationBrightness = 50
exit = False

# ===========================================================================
# mqtt config
# ===========================================================================
mqttHost: str = constant.MQTT_HOST
mqttPort: int = constant.MQTT_PORT
mqttClientId = f"mqtt-{scriptName}-{random.randint(0, 1000)}"

def on_connect(client, userdata, flags, reason_code, properties):
  if args.verbose:
    print("MQTT Connection Success")
    print("MQTT Subscribe")

  client.subscribe(constant.MQTT_TOPIC_ANIMATION_START)
  client.subscribe(constant.MQTT_TOPIC_ANIMATION_STOP)

  if reason_code == 0:
    logging.info("MQTT Connection Success")
  else:
    logging.critical("Failed to connect, return code %d\n", reason_code)

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
  logging.info("Disconnected with result code: %s", reason_code)

  reconnect_count, reconnect_delay = 0, constant.MQTT_FIRST_RECONNECT_DELAY

  while reconnect_count < constant.MQTT_MAX_RECONNECT_COUNT:
    logging.info("Reconnecting in %d seconds...", reconnect_delay)
    time.sleep(reconnect_delay)

    try:
      mqtt.reconnect()
      logging.info("Reconnected successfully!")
      return
    except ConnectionError as err:
      logging.error("%s. Reconnect failed. Retrying...", err)

    reconnect_delay *= constant.MQTT_RECONNECT_RATE
    reconnect_delay = min(reconnect_delay, constant.MQTT_MAX_RECONNECT_DELAY)
    reconnect_count += 1
  logging.info("Reconnect failed after %s attempts. Exiting...", reconnectCount)

def on_publish(client, userdata, msg, reason_code, properties):
  if args.verbose:
    print("MQTT Publish")

  logging.debug("Publish: %s", reason_code)

def on_connect_fail(client, userdata):
  if args.verbose:
    print("MQTT Connection Fail")
  
  logging.warning("MQTT connexion fail: %s", reason_code)

def on_message(client, userdata, msg):
  global animation, animationParams, animationBrightness, animationTime, beginloopTime, loopTime

  if args.verbose:
    print("MQTT onMessage")
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
  
  logging.debug(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

  if msg.topic == constant.MQTT_TOPIC_ANIMATION_START:

    payload = json.loads(msg.payload.decode("utf-8"))
    animation = payload["name"]
    animationParams = payload["parameters"]
    animationBrightness = payload["brightness"]
    animationTime = payload["time"]

    beginloopTime = time.time()
    loopTime = time.time()

    if args.verbose:
      print("Start animation " + animation)
      print("Reset " + animation + " animation time")

    logging.info("Set animation " + animation +  " and reset time")

    time.sleep(1)

  elif msg.topic == constant.MQTT_TOPIC_ANIMATION_STOP:

    if args.verbose:
      print("Stop animation")

    logging.info("Stop animation")

    animation = 'none'
    time.sleep(1)

def colorToTuple(color):
  if type(color) is list:
    colors = []
    for colorStr in color:
      colors.append(colorToTuple(colorStr))
    return colors

  if color == "WHITE":
    return WHITE
  elif color == "RED":
    return RED
  elif color == "YELLOW":
    return YELLOW
  elif color == "ORANGE":
    return ORANGE
  elif color == "GREEN":
    return GREEN
  elif color == "TEAL":
    return TEAL
  elif color == "CYAN":
    return CYAN
  elif color == "BLUE":
    return BLUE
  elif color == "PURPLE":
    return PURPLE
  elif color == "MAGENTA":
    return MAGENTA
  elif color == "BLACK":
    return BLACK
  elif color == "GOLD":
    return GOLD
  elif color == "PINK":
    return PINK
  elif color == "AQUA":
    return AQUA
  elif color == "JADE":
    return JADE
  elif color == "AMBER":
    return AMBER
  elif color == "OLD_LACE":
    return OLD_LACE
  elif color == "RGBW_WHITE_RGB":
    return RGBW_WHITE_RGB
  elif color == "RGBW_WHITE_W":
    return RGBW_WHITE_W
  elif color == "RGBW_WHITE_RGBW":
    return RGBW_WHITE_RGBW
  elif color == "RAINBOW":
    return RAINBOW

  return BLACK

pixels = neopixel.NeoPixel(board.D12, 24, brightness=0.5, auto_write=False, pixel_order="GRB")
pixels.fill((0, 0, 0))
pixels.show()

if __name__ == "__main__":

  logging.info("Init --------------------------------")

  if args.verbose:
    print("MQTT lauch")
    print("MQTT broker " + mqttHost)
    print("MQTT client id " + mqttClientId)

  # connect to mqtt server
  oMqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, mqttClientId)
  oMqttClient.on_connect = on_connect
  oMqttClient.on_message = on_message
  oMqttClient.on_disconnect = on_disconnect
  oMqttClient.on_publish = on_publish
  oMqttClient.on_connect_fail = on_connect_fail
  oMqttClient.connect(mqttHost, mqttPort)

  #threading.Thread(
  #    target=oMqttClient.loop_forever, name="MQTT_Updater", daemon=True
  #).start()
  
  oMqttClient.loop_start()

  pixels.fill((0, 0, 0))
  pixels.show()

  currentAnimation = ''
  beginloopTime = time.time()
  loopTime = time.time()
  oAnim = None

  while True:
    try:

      #print("animation " + currentAnimation + ' / ' + animation)
      newAnimation = (currentAnimation != animation) or (currentAnimation == 'static') or (currentAnimation == 'progress')

      if newAnimation:
        logging.info("New animation " + animation + " detected")

      try:

        if animation == 'none':

          pixels.fill((0, 0, 0))
          pixels.show()

        elif animation == 'progress':

          if newAnimation:
            oAnim = None
            logging.info("Init progress: " + animation)

            color = colorToTuple(animationParams['color'])
            percent = animationParams['percent']
            numPixels = len(pixels)
            
            onPixels = round((percent * numPixels / 100))

            if args.verbose:
              print("set on " + str(onPixels) + " pixels for " + str(percent) + " percent")

            for i in range(numPixels):
              if i<onPixels:
                pixels[i] = color
              else:
                pixels[i] = (0, 0, 0)

            pixels.show()

        elif animation == 'static':
          oAnim = None
          if newAnimation:
            logging.info("Init static: " + animation)

            color = colorToTuple(animationParams['color'])
            onPixels = animationParams['size']
            numPixels = len(pixels)

            for i in range(numPixels):
              if i<onPixels:
                pixels[i] = color
              else:
                pixels[i] = (0, 0, 0)

            pixels.show()

        elif animation == 'chase':
          """
          Chase pixels in one direction in a single color, like a theater marquee sign.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation speed rate in seconds, e.g. ``0.1``.
          :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          :param size: Number of pixels to turn on in a row.
          :param spacing: Number of pixels to turn off in a row.
          :param reverse: Reverse direction of movement.
          """
          if newAnimation:
            logging.info("Init Chase: " + animation)
            oAnim = Chase(pixels,
                          speed=animationParams['speed'],
                          color=colorToTuple(animationParams['color']),
                          size=animationParams['size'],
                          spacing=animationParams['spacing'],
                          reverse=animationParams['reverse'])
        
        elif animation == 'volume':
          """
          Animate the brightness and number of pixels based on volume.
          :param pixel_object: The initialised LED object.
          :param float speed: Animation update speed in seconds, e.g. ``0.1``.
          :param brightest_color: Color at max volume ``(r, g, b)`` tuple, or ``0x000000`` hex format
          :param decoder: a MP3Decoder object that the volume will be taken from
          :param float max_volume: what volume is considered maximum where everything is lit up
          """
          if newAnimation:
            logging.info("Init Volume: " + animation)
        
            oAnim = Volume(pixels,
                           speed=animationParams['speed'],
                           color=colorToTuple(animationParams['color']),
                           brightest_color=colorToTuple(animationParams['brightest_color']),
                           max_volume=animationParams['max_volume'])
        
        elif animation == 'sparklepulse':
          """
          Combination of the Sparkle and Pulse animations.
        
          :param pixel_object: The initialised LED object.
          :param int speed: Animation refresh rate in seconds, e.g. ``0.1``.
          :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          :param period: Period to pulse the LEDs over.  Default 5.
          :param breath: Duration to hold minimum and maximum intensity. Default 0.
          :param max_intensity: The maximum intensity to pulse, between 0 and 1.0.  Default 1.
          :param min_intensity: The minimum intensity to pulse, between 0 and 1.0.  Default 0.
          """
          if newAnimation:
            logging.info("Init SparklePulse: " + animation)
            oAnim = SparklePulse(pixels,
                                 speed=animationParams['speed'],
                                 color=colorToTuple(animationParams['color']),
                                 period=animationParams['period'],
                                 breath=animationParams['breath'],
                                 max_intensity=animationParams['max_intensity'],
                                 min_intensity=animationParams['min_intensity'])
        
        elif animation == 'sparkle':
          """
          Sparkle animation of a single color.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation speed in seconds, e.g. ``0.1``.
          :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          :param num_sparkles: Number of sparkles to generate per animation cycle.
          :param mask: array to limit sparkles within range of the mask
          """
          if newAnimation:
            logging.info("Init Sparkle: " + animation)
            oAnim = Sparkle(pixels,
                            speed=animationParams['speed'],
                            num_sparkles=animationParams['num_sparkles'],
                            color=colorToTuple(animationParams['color']))
        
        elif animation == 'rainbowsparkle':
          """Rainbow sparkle animation.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation refresh rate in seconds, e.g. ``0.1``.
          :param float period: Period to cycle the rainbow over in seconds.  Default 5.
          :param int num_sparkles: The number of sparkles to display. Defaults to 1/20 of the pixel
                                   object length.
          :param float step: Color wheel step.  Default 1.
          :param str name: Name of animation (optional, useful for sequences and debugging).
          :param float background_brightness: The brightness of the background rainbow. Defaults to
                                              ``0.2`` or 20 percent.
          :param bool precompute_rainbow: Whether to precompute the rainbow.  Uses more memory.
                                          (default True).
          """
          if newAnimation:
            logging.info("Init RainbowSparkle: " + animation)
            oAnim = RainbowSparkle(pixels,
                                   speed=animationParams['speed'],
                                   period=animationParams['period'],
                                   num_sparkles=animationParams['num_sparkles'],
                                   step=animationParams['step'],
                                   name=animationParams['name'],
                                   background_brightness=animationParams['background_brightness'],
                                   precompute_rainbow=animationParams['precompute_rainbow'])
        
        elif animation == 'solid':
          """
          A solid color.
        
          :param pixel_object: The initialised LED object.
          :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          """
          if newAnimation:
            logging.info("Init Solid: " + animation)
            oAnim = Solid(pixels,
                          color=colorToTuple(animationParams['color']))
        
        elif animation == 'comet':
          """
          A comet animation.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation speed in seconds, e.g. ``0.1``.
          :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          :param background_color: Background color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
                                   Defaults to BLACK.
          :param int tail_length: The length of the comet. Defaults to 25% of the length of the
                                  ``pixel_object``. Automatically compensates for a minimum of 2 and a
                                  maximum of the length of the ``pixel_object``.
          :param bool reverse: Animates the comet in the reverse order. Defaults to ``False``.
          :param bool bounce: Comet will bounce back and forth. Defaults to ``False``.
          :param Optional[string] name: A human-readable name for the Animation.
                                        Used by the to string function.
          :param bool ring: Ring mode.  Defaults to ``False``.
          """
          if newAnimation:
            logging.info("Init Comet: " + animation)
            oAnim = Comet(pixels,
                          speed=animationParams['speed'],
                          background_color=animationParams['background_color'],
                          tail_length=animationParams['tail_length'],
                          reverse=animationParams['reverse'],
                          bounce=animationParams['bounce'],
                          color=colorToTuple(animationParams['color']))
        
        elif animation == 'colorcycle':
          """
          Animate a sequence of one or more colors, cycling at the specified speed.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation speed in seconds, e.g. ``0.1``.
          :param colors: A list of colors to cycle through in ``(r, g, b)`` tuple, or ``0x000000`` hex
                         format. Defaults to a rainbow color cycle.
          :param start_color: An index (from 0) for which color to start from. Default 0 (first color).
          """
          if newAnimation:
            logging.info("Init ColorCycle: " + animation)

            colors = colorToTuple(animationParams['colors'])
            pprint.pprint(colors)

            oAnim = ColorCycle(pixels,
                               speed=animationParams['speed'],
                               start_color=animationParams['start_color'],
                               colors=colorToTuple(animationParams['colors']))
        
        elif animation == 'blink':
          """
          Blink a color on and off.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation speed in seconds, e.g. ``0.1``.
          :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          """
          if newAnimation:
            logging.info("Init Blink: " + animation)
            oAnim = Blink(pixels,
                          speed=animationParams['speed'],
                          color=colorToTuple(animationParams['color']))
        
        elif animation == 'customcolorchase':
          """
          Chase pixels in one direction, like a theater marquee with Custom Colors
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation speed rate in seconds, e.g. ``0.1``.
          :param colors: Animation colors in list of `(r, g, b)`` tuple, or ``0x000000`` hex format
          :param size: Number of pixels to turn on in a row.
          :param spacing: Number of pixels to turn off in a row.
          :param reverse: Reverse direction of movement.
          """
          if newAnimation:
            logging.info("Init CustomColorChase: " + animation)
            oAnim = CustomColorChase(pixels,
                                     speed=animationParams['speed'],
                                     size=animationParams['size'],
                                     reverse=animationParams['reverse'],
                                     spacing=animationParams['spacing'],
                                     colosrs=[colorToTuple(animationParams['color'])])
        
        elif animation == 'rain':
          """
          Droplets of rain.
        
          :param grid_object: The initialised PixelGrid object.
          :param float speed: Animation speed in seconds, e.g. ``0.1``.
          :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          :param count: Number of sparkles to generate per animation cycle.
          :param length: Number of pixels per raindrop (Default 3)
          :param background: Background color (Default BLACK).
          """
          if newAnimation:
            logging.info("Init Rain: " + animation)
            oAnim = Rain(pixels,
                         speed=animationParams['speed'],
                         count=animationParams['count'],
                         length=animationParams['length'],
                         background=colorToTuple(animationParams['background']),
                         color=colorToTuple(animationParams['color']))
        
        elif animation == 'multicolorcomet':
          """
          A multi-color comet animation.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation speed in seconds, e.g. ``0.1``.
          :param colors: Animation colors in a list or tuple of entries in
                                  ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          :param int tail_length: The length of the comet. Defaults to 25% of the length of the
                                  ``pixel_object``. Automatically compensates for a minimum of 2 and a
                                  maximum of the length of the ``pixel_object``.
          :param bool reverse: Animates the comet in the reverse order. Defaults to ``False``.
          :param bool bounce: Comet will bounce back and forth. Defaults to ``True``.
          :param Optional[string] name: A human-readable name for the Animation.
                                        Used by the to string function.
          :param bool ring: Ring mode.  Defaults to ``False``.
          :param bool off_pixels: Turn pixels off after the animation passes them. Defaults to ``True``.
                                  Setting to False will result in all pixels not currently in the comet
                                  to remain on and set to a color after the comet passes.
          """
          if newAnimation:
            logging.info("Init MulticolorComet: " + animation)
            oAnim = MulticolorComet(pixels,
                                    speed=animationParams['speed'],
                                    tail_length=animationParams['tail_length'],
                                    reverse=animationParams['reverse'],
                                    bounce=animationParams['bounce'],
                                    off_pixels=animationParams['off_pixels'],
                                    colors=[colorToTuple(animationParams['color'])])
        
        elif animation == 'pulse':
          """
          Pulse all pixels a single color.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation refresh rate in seconds, e.g. ``0.1``.
          :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          :param period: Period to pulse the LEDs over.  Default 5.
          :param breath: Duration to hold minimum and maximum intensity levels. Default 0.
          :param min_intensity: Lowest brightness level of the pulse. Default 0.
          :param max_intensity: Highest brightness elvel of the pulse. Default 1.
          """
          if newAnimation:
            logging.info("Init Pulse: " + animation)
            oAnim = Pulse(pixels,
                          speed=animationParams['speed'],
                          period=animationParams['period'],
                          breath=animationParams['breath'],
                          min_intensity=animationParams['min_intensity'],
                          max_intensity=animationParams['max_intensity'],
                          color=colorToTuple(animationParams['color']))
        
        elif animation == 'rainbow':
          """
          The classic rainbow color wheel.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation refresh rate in seconds, e.g. ``0.1``.
          :param float period: Period to cycle the rainbow over in seconds.  Default 5.
          :param float step: Color wheel step.  Default 1.
          :param str name: Name of animation (optional, useful for sequences and debugging).
          :param bool precompute_rainbow: Whether to precompute the rainbow.  Uses more memory.
                                          (default True).
          """
          if newAnimation:
            logging.info("Init Rainbow: " + animation)
            oAnim = Rainbow(pixels,
                            speed=animationParams['speed'],
                            period=animationParams['period'],
                            step=animationParams['step'],
                            name=animationParams['name'],
                            precompute_rainbow=animationParams['precompute_rainbow'])
        
        elif animation == 'rainbowchase':
          """
          Chase pixels in one direction, like a theater marquee but with rainbows!
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation speed rate in seconds, e.g. ``0.1``.
          :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
          :param size: Number of pixels to turn on in a row.
          :param spacing: Number of pixels to turn off in a row.
          :param reverse: Reverse direction of movement.
          :param step: How many colors to skip in ``colorwheel`` per bar (default 8)
          """
          if newAnimation:
            logging.info("Init RainbowChase: " + animation)
            oAnim = RainbowChase(pixels,
                                 speed=animationParams['speed'],
                                 size=animationParams['size'],
                                 spacing=animationParams['spacing'],
                                 reverse=animationParams['reverse'],
                                 step=animationParams['step'])
        
        elif animation == 'rainbowcomet':
          """
          A rainbow comet animation.
        
          :param pixel_object: The initialised LED object.
          :param float speed: Animation speed in seconds, e.g. ``0.1``.
          :param int tail_length: The length of the comet. Defaults to 10. Cannot exceed the number of
                                  pixels present in the pixel object, e.g. if the strip is 30 pixels
                                  long, the ``tail_length`` cannot exceed 30 pixels.
          :param bool reverse: Animates the comet in the reverse order. Defaults to ``False``.
          :param bool bounce: Comet will bounce back and forth. Defaults to ``False``.
          :param int colorwheel_offset: Offset from start of colorwheel (0-255).
          :param int step: Colorwheel step (defaults to automatic).
          :param bool ring: Ring mode.  Defaults to ``False``.
          """
          if newAnimation:
            logging.info("Init RainbowComet: " + animation)
            oAnim = RainbowComet(pixels,
                                 speed=animationParams['speed'],
                                 tail_length=animationParams['tail_length'],
                                 reverse=animationParams['reverse'],
                                 colorwheel_offset=animationParams['colorwheel_offset'],
                                 step=animationParams['step'])

      except Exception as err:
        if args.verbose:
          print(err, ". create animation " + animation + " failed.")

        logging.error("%s. create animation " + animation + " failed.", err)
        animation = 'none'
        newAnimation = False
        pass

      if newAnimation:
        if args.verbose:
          print("Is new animation " + animation)

        logging.info("Is new animation " + animation)

        if animation != 'none':

          if args.verbose:
            print("Reset " + animation + " animation time")

          pixels.brightness = animationBrightness / 255.0
          logging.info("Set brightness to " + str(pixels.brightness))

          logging.info("Reset " + animation + " animation time")

          beginloopTime = time.time()
          loopTime = time.time()

        time.sleep(0.25)

      if animation != 'none':
        loopTime = time.time()

        if oAnim is not None:
          
          if animation == 'energy':
            updateReactive()
          elif animation == 'static':
            time.sleep(0.25)
          else:
            oAnim.animate()

      currentAnimation = animation
      if loopTime - beginloopTime >= animationTime:

        if animation != 'none':
          if args.verbose:
            print("Animation " + animation + " time is over")
          
          logging.info("Animation " + animation + " time is over")

        animation = 'none'

      time.sleep(0.05)

    except KeyboardInterrupt:
      pixels.fill((0, 0, 0))
      pixels.show()
      exit()
    except:
      if args.verbose:
        print("Unexpected error:", sys.exc_info()[0])
      raise
