import pyautogui
from pynput.mouse import Listener

# https://nitratine.net/blog/post/how-to-get-mouse-clicks-with-python/
# https://www.geeksforgeeks.org/mouse-keyboard-automation-using-python/

# get resolution of display
print(pyautogui.size())

def on_click(x, y, button, pressed):
    if pressed:
        print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
    return

def on_move(x, y):
    # print('Pointer moved to {0}'.format((x, y)))
    return

def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up',(x, y)))
    return

with Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll) as listener:
    listener.join()