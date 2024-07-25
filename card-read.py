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

  args = parser.parse_args()

  payload_bytes = []
  for block in constant.BLOCKS:
    success, datas = readBlock(block)
    if success:
      payload_bytes.extend(datas)

  payload = smartcard.util.toASCIIString(payload_bytes).rstrip(".!")

  if args.pretty:
    print(json.dumps(json.loads(payload), indent=2))
  else:
    print(payload)
