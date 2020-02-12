import pyautogui as pyauto
from pynput import keyboard
from time import sleep
from datetime import date
import tkinter as tk


# failsafe - mouse cursor to top left corner


def test():
    print('Test')





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


ctrls = 0
running = False
file_name = 'automation1'


def main():
    def on_press_execute(key):
        global ctrls
        global running

        print(ctrls)
        ctrls += 1
        main_text.delete('1.0', tk.END)
        main_text.insert(tk.END, 'Workflow: {}'.format(ctrls))
        output = str(key).strip('\'')
        # if 'Key.ctrl_r' in output:
        #     ctrls += 1
        #     print(ctrls)
        # if 'Key.ctrl_r' in output and ctrls >= 3:  # toggle running
        #     ctrls = 0
        #     running = True
        #     print('Running')
        #     # scan()

    def impending_action(action, workflow_name_entry):
        if action == 'record':
            output = 'Primed to record actions for Workflow \'{}\'...'.format(workflow_name_entry)
            with keyboard.Listener(on_press=on_press_execute) as listener:
                listener.join()
        # elif action == 'execute':
        #     output = 'Primed to execute actions for Workflow \'{}\'...'.format(workflow_name_entry)
        #     with keyboard.Listener(on_press=on_press_execute) as listener:
        #         listener.join()
        else:
            print('Unknown action called (not execution nor record)')
        print(output)
        workflow_name.set(workflow_name_entry)
        main_text.delete('1.0', tk.END)
        main_text.insert(tk.END, 'Workflow: {}'.format(output))

    m = tk.Tk()
    m.title('Automation Tool')
    tk.Label(m, text='Automation Tool').grid(row=0, column=1, columnspan=6)

    tk.Button(m, text='Record', width=25, command=lambda: impending_action('record', workflow_name_entry.get())).grid(row=1, column=1)
    m.grid_columnconfigure(1, weight=1)
    tk.Label(m, text='', width=10).grid(row=1, column=2)
    tk.Label(m, text='Workflow name:').grid(row=1, column=3)
    workflow_name_entry = tk.Entry(m)
    workflow_name_entry.grid(row=1, column=4)
    workflow_name = tk.StringVar()
    tk.Label(m, text='', width=10).grid(row=1, column=5)
    tk.Button(m, text='Execute', width=25, command=lambda: impending_action('execute', workflow_name_entry.get())).grid(row=1, column=6)
    m.grid_columnconfigure(6, weight=1)

    main_text = tk.Text(m)
    main_text.grid(row=2, column=1, columnspan=6)
    tk.Button(m, text='Quit', width=25, command=m.destroy).grid(row=3, column=6)
    m.grid_rowconfigure(3, weight=1)
    m.mainloop()


if __name__ == "__main__":
    main()
