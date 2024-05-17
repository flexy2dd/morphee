# ===========================================================================
# Tools
# ===========================================================================
import threading
import functools
import time

def isEmptyString(myString):
  return myString is None or len(myString.strip()) == 0

def isEmptyInt(myInt):
  return myInt is None or myInt == 0

def isEmptyFloat(myFloat):
  return myFloat is None or myFloat <= 0.0

def isEmpty(myVar):
  if myVar==None:
    return True

  if type(myVar) is str:
    return isEmptyString(myVar)
  elif type(myVar) is int:
    return isEmptyInt(myVar)
  elif type(myVar) is float:
    return isEmptyFloat(myVar)

  return False

class PeriodicTimer(object):
  def __init__(self, interval, callback):
    self.interval = interval

    @functools.wraps(callback)
    def wrapper(*args, **kwargs):
      result = callback(*args, **kwargs)
      if result:
        self.thread = threading.Timer(self.interval, self.callback)
        self.thread.daemon = True
        self.thread.start()

    self.callback = wrapper

  def start(self):
    self.thread = threading.Timer(self.interval, self.callback)
    self.thread.daemon = True
    self.thread.start()

  def cancel(self):
    self.thread.cancel()

