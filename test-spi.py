# spi_test05 tlfong01 2019apr07hkt2043 ***

# Computer = Rpi3B+
# Linux    = $ hostnamectl = raspberrypi Raspbian GNU/Linux 9 (stretch) Linux 4.14.34-v7+ arm 
# Python   = >>> sys.version = 3.5.3 Jan 19 2017

# Test 1   - repeatSendByte() - SPI port repeatedly send out single bytes.  
# Function - Repeat many times sending a byte, pause after each byte.

# Test 2   - loopBackTest()   - SPI port send and receive one byte.
# Function - Send one byte to MSOI and read it back from MISO. 
# Setup    - Connet MOSI pin to MISO pin to form a loop.

from   time import sleep
import spidev

spiPort0 = spidev.SpiDev()
spiPort0.open(0,0)
spiPort0.max_speed_hz = 100000

def spiSendRecvOneByte(spiPort, sendByte):
    sendByteArray = [sendByte]
    recvByteArray = spiPort.xfer(sendByteArray)    
    return recvByteArray

def repeatSendOneByte(spiPort, sendByte, pauseTimeBetweenBytes, repeatCount):
    print('\nBegin repeatSendByte(),....')
    for i in range(repeatCount):
        spiSendRecvOneByte(spiPort, sendByte)
        sleep(pauseTimeBetweenBytes)
    print('End   repeatSendByte().')
    return

def loopBackOneByte(spiPort, sendByte):
    recvByteArray     = spiSendRecvOneByte(spiPort, sendByte)
    recvByte          = recvByteArray[0]

    print('\nBegin testLoopbackOneByte(),....')
    #print('')
    print('      sendByte  = ', hex(sendByte))
    print('      recvByte  = ', hex(recvByte))
    #print('')
    print('End   testLoopbackOneByte(),....')
    return

def testRepeatSendOneByte():
    repeatSendOneByte(spiPort0, 0x5b, 0.0001, 20000000)
    return

def testLoopbackOneByte():
    loopBackOneByte(spiPort0, 0x5b)
    return

#testRepeatSendOneByte()
testLoopbackOneByte()

''' Smple output tlfong 01 2019apr07hkt2047
Begin testLoopbackOneByte(),....
      sendByte  =  0x5b
      recvByte  =  0x5b
End   testLoopbackOneByte(),....
'''

# *** End ***
