import pyautogui as pyauto
from pynput import keyboard, mouse
from time import sleep
import pandas as pd
from datetime import date
import tkinter as tk


# failsafe - mouse cursor to top left corner

df = pd.read_csv('ctrl_keys_ref.csv', names=['Translation', 'Code'])
df = df.set_index('Code')
capslock = False
ctrls = 0
previous_base_key = False


def record():
    pass


def execute():
    with open('{}.txt'.format(workflow_name), 'r') as record_file:
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


def clear_file():
    with open('{}.txt'.format(workflow_name), 'w') as record_file:
        record_file.write('')


def output_to_file(output='', end='\n'):
    output = output + end
    with open('{}.txt'.format(workflow_name), 'a') as record_file:
        record_file.write(''.join(output))
    print(output, end='')


def on_press_recording(key):
    global capslock
    global ctrls
    global recording
    global previous_base_key
    output = str(key).strip('\'')
    if recording:
        if output == 'Key.caps_lock':  # if capslock pressed, swap capslock state
            capslock = not capslock
        if output == 'Key.space':  # if capslock pressed, swap capslock state
            output = ' '
        if not output.startswith('Key'):  # i.e., if output is alphanumeric
            if capslock:
                output = output.swapcase()
        if (output.startswith('\\') and output != '\\\\') or (output.startswith('<') and output.endswith('>')):
            output = 'CTRL+{}'.format(df['Translation'][output.replace('<', '').replace('>', '')])
        if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
            output_to_file('\\', end='')
            output = ''
        if output == '\"\'\"':
            output = '\''
        if (not output.startswith('Key.shift')) and (not output.startswith('Key.ctrl')) and (not output.startswith('Key.caps_lock')):  # ignore shift and ctrl keys
            if 'key' in output.lower() or 'ctrl' in output.lower():
                output = '`````' + output
                if previous_base_key:
                    output_to_file()
                output_to_file(output)
                previous_base_key = False
            else:
                previous_base_key = True
                output_to_file(output, end='')
    if 'Key.ctrl_r' in output:
        ctrls += 1
        if not recording:
            print('{}  '.format(ctrls), end='')
    if 'Key.ctrl_r' in output and ctrls >= 3:  # toggle recording
        ctrls = 0
        recording = not recording
        print()
        print('RECORDING = {}'.format(recording))


def on_click_recording(x, y, button, pressed):
    if recording:
        if pressed:
            if previous_base_key:
                output_to_file()
            output_to_file('`````{} clicked at ({}, {})'.format(button, x, y))


def on_scroll_recording(x, y, dx, dy):
    if recording:
        if previous_base_key:
            output_to_file()
        output_to_file('`````Scrolled {} at {}'.format('down' if dy < 0 else 'up', (x, y)))
    return


def on_move_recording(x, y):
    # if recording:
    #     if previous_base_key:
    #         output_to_file()
    #     output_to_file('`````Moved to {}'.format((x, y)))
    return



# def on_press_recording(key):
#     global ctrls
#     global running
#
#     output = str(key).strip('\'')
#     if 'Key.ctrl_r' in output:
#         ctrls += 1
#         print('{}  '.format(ctrls), end='')
#     if 'Key.ctrl_r' in output and ctrls >= 3:  # toggle running
#         ctrls = 1
#         running = True
#         print()
#         print('\tExecuting')
#         record()


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
            recording_warning = 'This will erase all contents in any files of the same name.'
            break
        elif action == 'e':
            action_status = 'execute'
            recording_warning = ''
            break

    confirmation = '_'
    while confirmation not in ['', 'y']:
        confirmation = '_'
        global workflow_name
        while True:
            workflow_name = input('Enter the workflow name: ')
            if '\\' not in workflow_name and '.' not in workflow_name and workflow_name != '':
                break
        if workflow_name.lower() == 'help':
            display_help()
        else:
            while confirmation != 'n':
                confirmation = input(
                    'The workflow name is \"{}\". {} Enter \'Yes\' to confirm or \'No\' to re-enter: '.format(workflow_name, recording_warning))
                if confirmation in ['', 'y']:
                    break

    print('Primed to {} actions for Workflow \"{}\"...'.format(action_status, workflow_name))
    print('\tNavigate to start of workflow and then press the right CTRL three times: ', end='')

    if action == 'e':
        with keyboard.Listener(on_press=on_press_execute) as listener:
            listener.join()
    elif action == 'r':
        global recording
        clear_file()
        recording = False
        with mouse.Listener(on_click=on_click_recording, on_scroll=on_scroll_recording, on_move=on_move_recording) as listener:
            with keyboard.Listener(on_press=on_press_recording) as listener:
                listener.join()


if __name__ == "__main__":
    main()
