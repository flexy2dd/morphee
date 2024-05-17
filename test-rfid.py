#!/usr/bin/env python

import RPi.GPIO as GPIO
from modules.mfrc522.MFRC522 import MFRC522
from modules.mfrc522.SimpleMFRC522 import SimpleMFRC522
from modules.mfrc522.BasicMFRC522 import BasicMFRC522

reader = SimpleMFRC522()
try:
        id, text = reader.read()
        print(id)
        print(text)
finally:
        GPIO.cleanup()

#from time import sleep
#import mfrc522
#
## Create an object of the MFRC522 class
#mfrc522 = mfrc522.MFRC522()
#
#def uid_to_num(uid):
#    n = 0
#    for i in range(0, 5):
#        n = n * 256 + uid[i]
#    return n
#
## Main function
#def main():
#    try:
#        while True:
#            # Scan for tags
#            (status, TagType) = mfrc522.MFRC522_Request(mfrc522.PICC_REQIDL)
#            if status != mfrc522.MI_OK:
#                return None, None
#
#            (status, uid) = mfrc522.MFRC522_Anticoll()
#            if status != mfrc522.MI_OK:
#                return None, None
#
#            id = uid_to_num(uid)
#            mfrc522.MFRC522_SelectTag(uid)
#            data = []
#            text_read = ''
#            if status == mfrc522.MI_OK:
#
#                block_num = 0
#
#                while True:
#                    block = mfrc522.MFRC522_Read(block_num)
#                    if block:
#                        data += block
#                        block_num = block_num + 4
#                    else:
#                        break
#
#                if data:
#                     text_read = ''.join(chr(i) for i in data)
#
#            mfrc522.MFRC522_StopCrypto1()
#
#            print("Hold a tag near the reader")
#            print("ID: %s\nText: %s" % (id,text_read))
#            sleep(5)
#
#    except KeyboardInterrupt:
#        print("Exiting...")
#        mfrc522.MFRC522_StopCrypto1()
#
#if __name__ == "__main__":
#    main()