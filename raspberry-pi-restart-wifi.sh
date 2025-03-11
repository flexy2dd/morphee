# Check wifi connection...
ping -c4 192.168.1.1 > /dev/null

# '$?' is the exit code of previous ping command.
# If exit code != 0 (failure)...
if [ $? != 0 ]
then
  echo "$(date): No network connection, restarting wlan0" >> /var/log/raspberry-pi-restart-wifi.log

  # deactivate wifi...
  /sbin/ifdown 'wlan0'
  sleep 5
  # Restart wifi...
  /sbin/ifup --force 'wlan0'
  #/sbin/shutdown -r now
fi
