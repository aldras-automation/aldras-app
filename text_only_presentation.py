import pyautogui as pyauto
from pynput import keyboard
from time import sleep
from datetime import date
import tkinter as tk


# failsafe - mouse cursor to top left corner


def record():
    pass


def execute():
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


def on_press_recording(key):
    global ctrls
    global running

    output = str(key).strip('\'')
    if 'Key.ctrl_r' in output:
        ctrls += 1
        print('{}  '.format(ctrls), end='')
    if 'Key.ctrl_r' in output and ctrls >= 3:  # toggle running
        ctrls = 1
        running = True
        print()
        print('\tExecuting')
        record()


def on_press_execute(key):
    global ctrls
    global running

    output = str(key).strip('\'')
    if 'Key.ctrl_r' in output:
        ctrls += 1
        print('{}  '.format(ctrls), end='')
    if 'Key.ctrl_r' in output and ctrls >= 3:  # toggle running
        ctrls = 1
        running = True
        print()
        print('\tExecuting')
        execute()


def display_help():
    print('This is the Help placeholder.')
    print()


ctrls = 0
running = False
file_name = 'automation1'


def main():
    print('Welcome to the Automation Tool by Noah Baculi, 2020')
    print('Remember, at any time to stop an automation execution, move the mouse cursor to the very left upper corner '
          'to trigger the failsafe.')
    print('For further instructions, enter \'Help\'.')
    print()
    while True:
        action = str(input('Input \'Record\' or \'Execute\' to select an option: '))[0]
        if action == 'h':
            display_help()
        elif action != 'r' and action != 'e':
            print('\tInvalid input, please enter \'Help\', \'Record\', or \'Execute\'')
        elif action == 'r':
            action_status = 'record'
            break
        elif action == 'e':
            action_status = 'execute'
            break

    confirmation = '_'
    while confirmation not in ['', 'y']:
        confirmation = '_'
        while True:
            workflow_name = input('Enter the workflow name: ')
            if '\\' not in workflow_name and '.' not in workflow_name and workflow_name != '':
                break
        if workflow_name.lower() == 'help':
            display_help()
        else:
            while confirmation != 'n':
                confirmation = input(
                    'The workflow name is \"{}\", enter \'Yes\' to confirm or \'No\' to re-enter: '.format(
                        workflow_name))
                if confirmation in ['', 'y']:
                    break

    print('Primed to {} actions for Workflow \"{}\"...'.format(action_status, workflow_name))
    print('\tNavigate to start of workflow and then press the right CTRL three times: ', end='')

    if action == 'e':
        with keyboard.Listener(on_press=on_press_execute) as listener:
            listener.join()


if __name__ == "__main__":
    main()
