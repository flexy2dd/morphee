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

def readTag(page):
  
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
          hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0xCA,0x00,0x00,0x00])
          print(smartcard.util.toHexString(response))
          print(hresult)

          # load key
          hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x82,0x00,0x00,0x06,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
          print(smartcard.util.toHexString(response))

          #auth block          
          hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x86,0x00,0x00,0x05,0x01,0x00,int(page),0x60,0x00])
          print(smartcard.util.toHexString(response))

          hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF, 0xB0, 0x00, int(page), 0x10])
          if hresult == SCARD_S_SUCCESS:
            print(smartcard.util.toHexString(response))
            print(smartcard.util.toASCIIString(response))

        else:
          print("NO_CARD")
      else:
        print("NO_READER")
    else:
      print("FAILED")

def readSector(sector):
  
    text_all = ''
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

            for block in range(0, 3):
            
              #auth block          
              hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x86,0x00,0x00,0x05,0x01,0x00,int(sector + block),0x60,0x00])
              if hresult == SCARD_S_SUCCESS:
            
                hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF, 0xB0, 0x00, int(sector + block), 0x10])
                if hresult == SCARD_S_SUCCESS:
                
                  response.pop()
                  response.pop()
            
                  text = smartcard.util.toASCIIString(response)
            
                  text_all += text

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
      text_all = ''

    return success, text_all

def readSectors(trailer_blocks):
  text_all = ''
  for trailer_block in trailer_blocks:
    id, text = self.readSector(trailer_block)
    text_all += text
  return id, text_all

#    readingLoop = 1
#    while(readingLoop):
#        try:
#            connection = reader.createConnection()
#            status_connection = connection.connect()
#            resp = connection.transmit(COMMAND)
#            print(smartcard.util.toHexString(response))
#
#            #Read command [FF, B0, 00, page, #bytes]
#            resp = connection.transmit([0xFF, 0xB0, 0x00, int(page), 0x04])
#            print(resp)
#            dataCurr = stringParser(resp)
#
#            #only allows new tags to be worked so no duplicates
#            if(dataCurr is not None):
#                print(dataCurr)
#                break
#            else:
#                print("Something went wrong. Page " + str(page))
#                break
#        except (Exception): 
#            print(Exception)
#            # if (waiting_for_beacon ==1):
#            #     continue
#            # else:
#            #     readingLoop=0
#            #     # print(str(e))
#            #     break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='write NFC tags')

    parser.add_argument('--url', nargs='?', help='Url.', required=True)
    parser.add_argument('--style', nargs='?', help='Style de musique. zen, nature, music (defaut), relax, love', default='music', choices = ['zen', 'music', 'relax', 'love'])
    parser.add_argument('--picto', nargs='?', help='Picto.', default='')
    parser.add_argument('--mode', nargs='?', help='Mode de lecture. once (defaut), shuffle, loop', default='once', choices = ['once', 'shuffle', 'loop'])
    parser.add_argument('--keep', nargs='?', type=int, help='Pistes à garder. (defaut 1)', default=1)
    parser.add_argument('--limit', nargs='?', type=int, help='Temps limite (minutes). (defaut 0)', default=0)
    parser.add_argument('--anim', nargs='?', help='Animation limineuse. none (defaut), sparklepulse', default='none', choices = ['none', 'sparklepulse'])
    
    args = parser.parse_args()

    payload = {
        "anim": args.anim,
        "style": args.style,
        "picto": args.picto,
        "mode": args.mode,
        "keep": args.keep,
        "limit": args.limit,
        "url": args.url
    }

    json_payload = json.dumps(payload)
    print(json_payload)
    print(smartcard.util.toASCIIBytes(json_payload))
    json_payload_bytes = smartcard.util.toASCIIBytes(json_payload)
    
    total_blocks = len(constant.BLOCKS) * 48
    diff_blocks = total_blocks - len(json_payload_bytes)

    print(len(json_payload_bytes))
    print(total_blocks)
    print(diff_blocks)

    for bcl in range(0, diff_blocks):
      json_payload_bytes.append(32)

    print(len(json_payload_bytes))
    print(json_payload_bytes)
    
    for block in constant.BLOCKS:
      data = []
      for bcl in range(0, 48):
        data.append(json_payload_bytes.pop(0))

      print(data)
 


#    if args.read:
#      for sector in args.read:
#
#        if "-" in sector:
#          start = int(sector.split("-")[0])
#          end = int(sector.split("-")[1])
#          text_all = ''
#          for new_sector in range(start, end+1):
#            success, text = readSector(BLOCKS[new_sector])
#            if success:
#              text_all += text
#
#          print(text_all)
#
#        else:
#          success, text_all = readSector(BLOCKS[int(sector)])
#          if success:
#            print(text_all)
#          else:
#            print('Failed')