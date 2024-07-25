# Python 3 code to demonstrate the
# working of bytes() on string
 
# initializing string
str1 = 'GeeksfÖr.Geeks'
 
# Giving ascii encoding and ignore error
print("Byte conversion with ignore error : " +
      str(bytes(str1, 'ascii', errors='ignore')))
 
# Giving ascii encoding and replace error
print("Byte conversion with replace error : " +
      str(bytes(str1, 'ascii', errors='replace')))
 
# Giving ascii encoding and strict error
# throws exception
print("Byte conversion with strict error : " +
      str(bytes(str1, 'ascii', errors='strict')))