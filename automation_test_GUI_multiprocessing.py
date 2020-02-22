import multiprocessing
import tkinter as tk
from time import sleep

import pyautogui as pyauto
from pynput import keyboard


# failsafe - mouse cursor to top left corner


def test():
    print('Test')


def on_press(key):
    global ctrls
    global running
    global recording
    output = str(key).strip('\'')
    print(recording)
    if recording:
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


def scan():
    with open('{}.txt'.format(file_name), 'r') as record_file:
        lines = record_file.readlines()
    pyauto.PAUSE = 0.5
    for line in lines:
        sleep(0.5)
        line = line.replace('\n', '')
        print(line)
        if line[0:5] == '`````':  # special keys
            if 'backspace' in line:
                pyauto.press('backspace')
            elif 'delete' in line:
                pyauto.press('del')
            elif 'Button.left' in line:
                coords = line.split('(')[-1].replace(')', '').replace(' ', '').split(',')
                pyauto.click(x=int(coords[0]), y=int(coords[1]), duration=0.5)
            elif 'enter' in line:
                pyauto.press('enter')
            elif 'tab' in line:
                pyauto.press('tab')
            elif 'home' in line:
                pyauto.press('home')
            elif 'end' in line:
                pyauto.press('end')
            elif 'up' in line:
                pyauto.press('up')
            elif 'down' in line:
                pyauto.press('down')
            elif 'left' in line:
                pyauto.press('left')
            elif 'right' in line:
                pyauto.press('right')
            elif 'esc' in line:
                pyauto.press('esc')
            elif 'alt_l' in line:
                pyauto.press('altleft')
            elif 'alt_r' in line:
                pyauto.press('altright')
            elif 'cmd' in line:
                pyauto.press('win')
            elif 'CTRL' in line:
                other_key = line.split('+')[-1]
                pyauto.hotkey('ctrl', other_key)
        else:
            pyauto.typewrite(line)

    print('\nComplete!')


def func_one(num):
    m = tk.Tk()
    m.title('Counting Seconds')
    tk.Label(m, text='Automation Tool').grid(row=0, column=1, columnspan=6)

    tk.Button(m, text='Record', width=25, command=record).grid(row=1, column=1)
    m.grid_columnconfigure(1, weight=1)
    tk.Label(m, text='', width=10).grid(row=1, column=2)
    tk.Label(m, text='Workflow name:').grid(row=1, column=3)
    workflow_name_entry = tk.Entry(m)
    workflow_name_entry.grid(row=1, column=4)
    workflow_name = tk.StringVar()
    tk.Label(m, text='', width=10).grid(row=1, column=5)
    tk.Button(m, text='Execute', width=25, command=lambda: execute(workflow_name_entry.get())).grid(row=1, column=6)
    m.grid_columnconfigure(6, weight=1)

    main_text = tk.Text(m)
    main_text.grid(row=2, column=1, columnspan=6)
    tk.Button(m, text='Quit', width=25, command=m.destroy).grid(row=3, column=6)
    m.bind('<Return>', execute)
    m.grid_rowconfigure(3, weight=1)
    m.mainloop()
    # popup = tk.Tk()
    # popup.wm_title("!")
    # label = ttk.Label(popup, text='yeah boi', font=("Helvetica", 10))
    # label.pack(side="top", fill="x", pady=10)
    # B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    # B1.pack()
    # popup.mainloop()


def func_two(num):
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def record():
    # await_trigger()
    global recording
    recording = not recording
    print(recording)
    return


def execute(workflow_name_entry):
    print('Workflow: {}'.format(workflow_name_entry))
    workflow_name.set(workflow_name_entry)
    main_text.delete('1.0', tk.END)
    main_text.insert(tk.END, 'Workflow: {}'.format(workflow_name_entry))
    pass


ctrls = 0
running = False
recording = False
file_name = 'automation1'

if __name__ == '__main__':
    multiprocessing.freeze_support()
    p1 = multiprocessing.Process(target=func_one, args=(1,))
    p2 = multiprocessing.Process(target=func_two, args=(2,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("Done!")
