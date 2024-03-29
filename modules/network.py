# module for getting some information of network
import os
import socket
import subprocess
import sys
import re
from pprint import pprint

if os.name != "nt":
  import fcntl
  import struct
  def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], encoding='utf8'))
        # Python 2.7: remove the second argument for the bytes call
      )[20:24])

def get_lan_ip():
  ip = socket.gethostbyname(socket.gethostname())
  if ip.startswith("127.") and os.name != "nt":
    interfaces = ["eth0","eth1","eth2","wlan0","wlan1","wifi0","ath0","ath1","ppp0"]
    for ifname in interfaces:
      try:
        ip = get_interface_ip(ifname)
        break;
      except IOError:
        pass
  return ip
    
def get_wifi_signal(interface = "wlan0"):
  command_line = "iwconfig " + interface + " 2> /dev/null | awk -F= '/Quality/ {print $2}' | awk '{print $1}'"

  proc = subprocess.Popen(command_line, stdout=subprocess.PIPE, universal_newlines=True,shell=True)
  out, err = proc.communicate()
  quality = 0
  if (re.search('/', out)):
    out = out.replace("\n", "")
    quality_level = out.split()[0].split('/')
    quality = str(int(round(float(quality_level[0]) / float(quality_level[1]) * 100)))

  return quality