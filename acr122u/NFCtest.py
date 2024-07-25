#! /usr/bin/env python
import re, argparse
from smartcard.scard import *
import smartcard.util
import datetime, sys

#hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
#
#if hresult == SCARD_S_SUCCESS:
#
#  hresult, readers = SCardListReaders(hcontext, [])
#
#  if len(readers) > 0:
#
#    reader = readers[0]
#
#    hresult, hcard, dwActiveProtocol = SCardConnect(
#        hcontext,
#        reader,
#        SCARD_SHARE_SHARED,
#        SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
#
#    if hresult == 0:
#      hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0xCA,0x00,0x00,0x00])
#
#      print(smartcard.util.toHexString(response))
#    else:
#      print("NO_CARD")
#  else:
#    print("NO_READER")
#else:
#  print("FAILED")

SECTOR_0 = 0
SECTOR_1 = 4
SECTOR_2 = 8
SECTOR_3 = 12
SECTOR_4 = 16
SECTOR_5 = 20
SECTOR_6 = 24
SECTOR_7 = 28
SECTOR_8 = 32
SECTOR_9 = 36
SECTOR_10	= 40
SECTOR_11	= 44
SECTOR_12	= 48
SECTOR_13	= 52
SECTOR_14	= 56
SECTOR_15	= 60

SECTORS = [SECTOR_0, SECTOR_1, SECTOR_2, SECTOR_3, SECTOR_4, SECTOR_5, SECTOR_6, SECTOR_7]

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
    parser = argparse.ArgumentParser(description='Read / write NFC tags')
    usingreader_group = parser.add_argument_group('usingreader')
    usingreader_group.add_argument('--usingreader', nargs=1, metavar='READER_ID', help='Reader to use [0-X], default is 0')
    read_group = parser.add_argument_group('read')
    read_group.add_argument('--read', nargs='+', help='Sectors to read. Can be a x-x range, or list of sectors')
    write_group = parser.add_argument_group('write')
    write_group.add_argument('--write', nargs=2, metavar=('PAGE', 'DATA'), help='Page number and hex value to write.')

    args = parser.parse_args()
    
    if args.read:
      for sector in args.read:

        if "-" in sector:
          start = int(sector.split("-")[0])
          end = int(sector.split("-")[1])
          text_all = ''
          for new_sector in range(start, end+1):
            success, text = readSector(SECTORS[new_sector])
            if success:
              text_all += text

          print(text_all)

        else:
          success, text_all = readSector(SECTORS[int(sector)])
          if success:
            print(text_all)
          else:
            print('Failed')