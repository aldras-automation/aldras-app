from time import sleep
import pyautogui
from pynput.mouse import Listener

def on_move(x, y):
    # print("Mouse moved to ({0}, {1})".format(x, y))
    return


def on_click(x, y, button, pressed):
    if pressed:
        # print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
        if -5 < x < 5 and -5 < y < 5:  # stop recording clicks when click in top left of screen
            listener.stop()
            return
        coord_list.append(["click", x, y])


def on_scroll(x, y, dx, dy):
    # print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))
    return


coord_list = []

with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
    listener.join()

print(coord_list)
print(len(coord_list))


sleep(2)

for coord_index in range(len(coord_list)):
    # print(str(coord_list[coord_index][0]) + ", " + str(coord_list[coord_index][1]))
    if coord_list[coord_index][0] == "click":
        pyautogui.click(coord_list[coord_index][1], coord_list[coord_index][2], duration=0.5)


#
# for ii in range(10):
#     pyautogui.typewrite(["tab"])
#     sleep(0.5)
