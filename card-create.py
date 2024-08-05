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

def writeBlock(block, datas):
  
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

          # load key
          hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x82,0x00,0x00,0x06,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
          if hresult == SCARD_S_SUCCESS:

            for sub in range(0, 3):
          
              #auth block
              hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x86,0x00,0x00,0x05,0x01,0x00,int(block + sub),0x60,0x00])
              if hresult == SCARD_S_SUCCESS:

                block_datas = [0xFF, 0xD6, 0x00, int(block + sub), 0x10]
                for bcl in range(0, 16):
                  block_datas.append(datas.pop(0))

                print('Ecriture du bloc: ' + str(block + sub))
                print(' - datas : ' + smartcard.util.toASCIIString(block_datas))
                hresult, response = SCardTransmit(hcard, dwActiveProtocol, block_datas)
                if hresult == SCARD_S_SUCCESS:
                  print(" - réussi.")
                else:
                  print(" - échoué.")
                  success = False
                  break

              else:
                print("Impossible d'authentifier le bloc.")
                success = False
                break

          else:
            print("Impossible de récuperer la clef.")
            success = False
        else:
          print("Pas de carte présente.")
          success = False
      else:
        print("Impossible de trouver un lecteur.")
        success = False
    else:
      print("FAILED")
      success = False

    return success

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Encodage cartes NFC')

  parser.add_argument('--pretty', help='Pretty print.', action='store_true', default=False)
  parser.add_argument('--write', help='Encode carte.', action='store_true', default=False)

  parser.add_argument('--url', nargs='?', help='Url.', required=True)
  parser.add_argument('--style', nargs='?', help='Style de musique. zen, nature, music (defaut), relax, love', default='music', choices = ['zen', 'music', 'relax', 'love'])
  parser.add_argument('--picto', nargs='?', help='Picto.', default='')

  parser.add_argument('--once', help='Lecture unique.', action='store_true', default=True)
  parser.add_argument('--shuffle', help='Mélange de la liste de lecture.', action='store_true', default=False)
  parser.add_argument('--loop', help='Lecture en boucle.', action='store_true', default=False)

  parser.add_argument('--keep', nargs='?', type=int, help='Pistes à garder. (defaut 1)', default=1)
  parser.add_argument('--limit', nargs='?', type=int, help='Temps limite (minutes). (defaut 0)', default=0)
  parser.add_argument('--anim', nargs='?', help='Animation limineuse. none (defaut), sparklepulse', default='none', choices = ['none', 'sparklepulse'])
  
  args = parser.parse_args()

  payload_object = {
      "anim": args.anim,
      "style": args.style,
      "picto": args.picto,
      "once": args.once,
      "shuffle": args.shuffle,
      "loop": args.loop,
      "keep": args.keep,
      "limit": args.limit,
      "url": args.url
  }

  payload = json.dumps(payload_object)
  json_payload_bytes = smartcard.util.toASCIIBytes(payload)
  
  total_blocks = len(constant.BLOCKS) * 48
  diff_blocks = total_blocks - len(json_payload_bytes)

  # complete paylod for all block
  for bcl in range(0, diff_blocks):
    json_payload_bytes.append(0)

  if args.write:

    print('Encodage de la carte...')

    for block in constant.BLOCKS:
      datas = []
      for bcl in range(0, 48):
        datas.append(json_payload_bytes.pop(0))

      success = writeBlock(block, datas)
      if not success:
        print("L'encodage de la carte a echoué.")
        break

    if success:
      print("L'encodage de la carte a réussi.")

  else:
    if args.pretty:
      print(json.dumps(payload_object, indent=2))
    else:
      print(payload)
