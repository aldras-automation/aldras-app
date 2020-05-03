import pyautogui as pyauto
import time

t0 = time.time()

var = None

for ii in range(1000000):
    var = 2

print(time.time()-t0)