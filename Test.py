import pyautogui as pyauto
import time

while 1:
    print(f'Mouse at: {tuple(pyauto.position())}')
    time.sleep(0.08)
