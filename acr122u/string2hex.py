from configparser import ConfigParser
  

s = "Hello World !"

senc = s.encode('utf-8') # ascii, utf-8
tenc = senc.hex()

sdec = senc.decode('utf-8')


print('Initial string:', s)
print('Encoded string: ', tenc)
print('Decoded string:', sdec)


# with open("state_parameters.ini", "r") as f:
#     lines = f.readlines()

#     for line in lines:
#         print(line)




configur = ConfigParser()
print (configur.read('state_parameters.ini'))
print ("Sections : ", configur.sections())
print ("Scanning frequency : ", configur.get('Scan Parameters','freq'))
# print ("Log Errors debugged ? : ", configur.getboolean('debug','log_errors'))
# print ("Port Server : ", configur.getint('server','port'))
# print ("Worker Server : ", configur.getint('server','nworkers'))

print(configur.items("Scan Parameters"))

k = configur.get("Scan Parameters", "freq")
k = round(float(k), 2)
print(type(k))
print(k)


ks = str(k)
print(type(ks))
print(len(ks))
print(ks)
