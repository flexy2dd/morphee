#! /usr/bin/env python
import re
import argparse
import datetime
import sys
import os
import re
import json
from smartcard.scard import *
import smartcard.util
from modules import constant

def readBlock(block):

  datas = []
  success = True

  hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)

  if hresult == SCARD_S_SUCCESS:

    hresult, readers = SCardListReaders(hcontext, [])

    if len(readers) > 0:

      reader = readers[0]

      hresult, hcard, dwActiveProtocol = SCardConnect(
          hcontext,
          reader,
          SCARD_SHARE_SHARED,
          SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)

      if hresult == SCARD_S_SUCCESS:

        # get id
        #hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0xCA,0x00,0x00,0x00])

        # load key
        hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x82,0x00,0x00,0x06,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
        if hresult == SCARD_S_SUCCESS:

          for sub in range(0, 3):

            #auth block
            hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x86,0x00,0x00,0x05,0x01,0x00,int(block + sub),0x60,0x00])
            if hresult == SCARD_S_SUCCESS:

              hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF, 0xB0, 0x00, int(block + sub), 0x10])
              if hresult == SCARD_S_SUCCESS:

                response.pop()
                response.pop()

                datas.extend(response)

              else:
                print("NO_READ")
                success = False
            else:
              print("NO_AUTH")
              success = False
        else:
          print("NO_KEY")
          success = False
      else:
        print("NO_CARD")
        success = False
    else:
      print("NO_READER")
      success = False
  else:
    print("FAILED")
    success = False

  if not success:
    datas = []

  return success, datas

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Read NFC tags')
  parser.add_argument('--pretty', help='Pretty print.', action='store_true')
  parser.add_argument('--command', help='Créer une ligne de commande.', action='store_true')

  args = parser.parse_args()

  ready = True
  payload_bytes = []
  for block in constant.BLOCKS:
    success, datas = readBlock(block)
    if success:
      payload_bytes.extend(datas)
    else:
      ready = False

  if ready:
    payload = smartcard.util.toASCIIString(payload_bytes).rstrip(".!")
    payload_object = json.loads(payload)

    if args.command:
      line = ''
      
      if "anim" in payload_object:
        line += ' --anim ' + payload_object["anim"]

      if "picto" in payload_object:
        if payload_object["picto"].strip() != "":
          line += ' --picto ' + payload_object["picto"]

      if "style" in payload_object:
        line += ' --style ' + payload_object["style"]

      if "shuffle" in payload_object:
        if payload_object["shuffle"]==1:
          line += ' --shuffle'

      if "once" in payload_object:
        if payload_object["once"]==1:
          line += ' --once'

      if "loop" in payload_object:
        if payload_object["limit"]==1:
          line += ' --loop'

      if "limit" in payload_object:
        line += ' --limit ' + str(payload_object["limit"])

      if "keep" in payload_object:
        line += ' --keep ' + str(payload_object["keep"])

      if "url" in payload_object:
        line += ' --url ' + payload_object["url"]

      print('card-create.py' + line)
    else:
      if args.pretty:
        print(json.dumps(payload_object, indent=2))
      else:
        print(payload)

  else:
    print("Read card FAILED")
