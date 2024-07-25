from smartcard.System import readers
import NFCReader as nfc

COMMAND = [0xFF, 0xCA, 0x00, 0x00, 0x00] #handshake cmd needed to initiate data transfer

# get all the available readers
r = readers()
print("Available readers:", r)


# Write something
r.readTag(5)


# nfc.writeTag(5, "bbbbbbbb")

r.readTag(5)
