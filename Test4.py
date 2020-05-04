import pyautogui as pyauto
import time
import math

t0 = time.time()

var = None

for ii in range(1000000):
    var = round(1.489238476234)

print(time.time()-t0)

pyauto.press('Win')