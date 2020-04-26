from screeninfo import get_monitors
import time
import pyautogui

for m in get_monitors():
    print(str(m))
print(get_monitors())
display_size = (sum([monitor.width for monitor in get_monitors()]), sum([monitor.height for monitor in get_monitors()]))
tot_height = sum([monitor.height for monitor in get_monitors()])
print(f'total display_size: {display_size}')
print(f'total height: {tot_height}')
print()
time.sleep(1)