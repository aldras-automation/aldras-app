import pyautogui as pyauto
import time
import math

#
var = 'asdfjwoidfasdf'
#

t0 = time.time()

for ii in range(10000):
    var1 = var.replace('yo', '')

print(time.time()-t0)
