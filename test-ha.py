import argparse
import time
import logging
import os
import pprint
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from pathlib import Path
from modules import speak
from modules import constant
from modules import core
from ha_mqtt_discoverable import Settings
from ha_mqtt_discoverable import DeviceInfo
from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo, Text, TextInfo

# ===========================================================================
# Param
# ===========================================================================
parser = argparse.ArgumentParser(description="Morphe manager service")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
parser.add_argument("-V", "--volume", help="volume (0 > 100)", type=int, default=10)
parser.add_argument("-s", "--sentence", help="sentence", type=str, default="Initialisation en cours...")
args = parser.parse_args()

scriptName = Path(__file__).stem
logging_level = 20
logging_path =  '.'
logging.basicConfig(filename=logging_path + '/' + scriptName + '.log', level=int(logging_level))

scriptName = Path(__file__).stem
oCore = core.core(scriptName)
oCore.verbose = True

# connect to mqtt server
oMqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, oCore.mqttClientId)
#oMqttClient.on_connect = on_connect
#oMqttClient.on_message = on_message
#oMqttClient.on_disconnect = on_disconnect
#oMqttClient.enable_logger = logging

if args.verbose:
  print('Start MQTT on ' + str(constant.MQTT_HOST) + ':' + str(constant.MQTT_PORT))

oMqttClient.connect(str(constant.MQTT_HOST), int(constant.MQTT_PORT))
oMqttClient.loop_start()

def my_callback(client: Client, user_data, message: MQTTMessage):
    text = message.payload.decode()
    #logging.info(f"Received {text} from HA")
    #do_some_custom_thing(text)
    # Send an MQTT message to confirm to HA that the text was changed
    my_text.set_text(text)

mqtt_settings = Settings.MQTT(client=oMqttClient)

# Define the device. At least one of `identifiers` or `connections` must be supplied
device_info = DeviceInfo(name="Morphee", identifiers="morphee")

# Information about the `text` entity
text_info = TextInfo(name="test", unique_id="morphee_ip", device=device_info)

text_info_settings = Settings(mqtt=mqtt_settings, entity=text_info)

# Define an optional object to be passed back to the callback
user_data = "Some custom data"

# Instantiate the text
my_text = Text(text_info_settings, my_callback, user_data)

# Set the initial text displayed in HA UI, publishing an MQTT message that gets picked up by HA
my_text.set_text("Some awesome text")

#oSpeak = speak.speak(
#  core = oCore,
#  logging = logging
#)
#oSpeak.verbose = True
#oSpeak.say(args.sentence, args.volume)

#while(True):
#  time.sleep(0.5)