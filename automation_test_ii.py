import multiprocessing
import tkinter as tk
from tkinter import ttk

from pynput import keyboard


def func_one(num):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text='yeah boi', font=("Helvetica", 10))
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()


def func_two(num):
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def on_press(key):
    global ctrls
    global running
    output = str(key).strip('\'')
    print(key)
    if 'Key.ctrl_r' in output:
        ctrls += 1
        # print(ctrls)
    if 'Key.ctrl_r' in output and ctrls >= 3:  # toggle running
        ctrls = 0
        running = True
        print('Complete')
        raise SystemExit()
        # sleep(1)
        # scan()


if __name__ == "__main__":
    p1 = multiprocessing.Process(target=func_one, args=(1,))
    p2 = multiprocessing.Process(target=func_two, args=(2,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Done!")
