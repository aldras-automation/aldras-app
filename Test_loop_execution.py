import pyautogui as pyauto

line = 'Key Backspace Tap'
key = line.lower().replace('key', '').replace('tap', '').replace(' ', '')
print(key)

pyauto.click(x=3774, y=968)
pyauto.hotkey('ctrl', 'a')
# pyauto.press(key)
