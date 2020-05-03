import math
import re
import time

import pandas as pd
import pyautogui as pyauto
from pynput import keyboard, mouse

# failsafe - mouse cursor to top left corner


df = pd.read_csv('data/ctrl_keys_ref.csv', names=['Translation', 'Code'])
df = df.set_index('Code')
capslock = False
ctrls = 0
drag_duration_scale = math.hypot(pyauto.size().width, pyauto.size().width)
type_interval = 0.02
mouse_duration = 0.5


def on_press_execute(key):
    global ctrls

    output = str(key).strip('\'')
    if 'Key.ctrl_r' in output:
        ctrls += 1
        print('{}  '.format(ctrls), end='')
    if 'Key.ctrl_r' in output and ctrls >= 3:
        ctrls = 0
        print()
        print('\tExecuting')
        execute()


def float_in(input_string):
    return float(re.findall(r'[-+]?\d*\.\d+|\d+', input_string)[0])


def execute():
    # time.sleep(1)
    with open('{}.txt'.format(workflow_name), 'r') as record_file:
        lines = record_file.readlines()
    pyauto.PAUSE = pause
    for line_orig in lines:
        line = line_orig.replace('\n', '').lower()
        print(line)

        if 'type' in line:  # 'type' command execution should be checked-for first because it may contain other command keywords
            pyauto.typewrite(
                line_orig.replace('\n', '').replace('Type: ', '').replace('type: ', '').replace('Type:', '').replace(
                    'type:', ''), interval=type_interval)

        elif 'sleep' in line:
            time.sleep(float_in(line))

        elif 'left-mouse' in line or 'right-mouse' in line:
            coords = coords_of(line)
            if 'right-mouse' in line:
                btn = 'right'
            else:
                btn = 'left'

            if 'tap' in line:
                pyauto.click(x=coords[0], y=coords[1], button=btn)
            elif 'press' in line:
                pyauto.mouseDown(x=coords[0], y=coords[1], button=btn)
            elif 'release' in line:
                pyauto.mouseUp(x=coords[0], y=coords[1], button=btn)

        elif 'hotkey' in line:  # 'hotkey' command execution should be checked-for before 'key' because 'key' is
            # contained in 'hotkey'
            hotkeys = line.replace('hotkey ', '').split('+')
            pyauto.hotkey(*hotkeys)  # the asterisk (*) unpacks the iterable list and passes each string as an argument

        elif 'key' in line:
            if 'tap' in line:
                key = line.replace('key', '').replace('tap', '').replace(' ', '')
                pyauto.press(key)
            elif 'press' in line:
                key = line.replace('key', '').replace('tap', '').replace(' ', '')
                pyauto.keyDown(key)
            elif 'release' in line:
                key = line.replace('key', '').replace('tap', '').replace(' ', '')
                pyauto.keyUp(key)

        elif 'mouse-move' in line:
            coords = coords_of(line)
            pyauto.moveTo(x=coords[0], y=coords[1], duration=mouse_duration)

        elif 'doubleclick' in line:
            coords = coords_of(line)
            pyauto.click(clicks=2, x=coords[0], y=coords[1], duration=mouse_duration)

        elif 'tripleclick' in line:
            coords = coords_of(line)
            pyauto.click(clicks=3, x=coords[0], y=coords[1], duration=mouse_duration)

    #     else:
    #         action = line.split('```')[1]
    #         key = line.split('```')[0].split('.')[1]
    #         if 'button.' in line:
    #             coords = line.split('(')[-1].replace(')', '').replace(' ', '').split(',')
    #             coords[0] = int(coords[0])
    #             coords[1] = int(coords[1])
    #             if 'press' in line:
    #                 pyauto.mouseDown(button=key, x=coords[0], y=coords[1])
    #                 down = coords
    #             elif 'release' in line:
    #                 # pyauto.mouseUp(button='left', x=int(coords[0]), y=int(coords[1]), duration=drag_duration)
    #                 drag_dist = math.hypot(down[0] - coords[0], down[1] - coords[1])
    #                 drag_duration = 0.5 * mouse_duration + (drag_dist / drag_duration_scale)
    #                 pyauto.moveTo(x=coords[0], y=coords[1], duration=drag_duration)
    #                 pyauto.mouseUp(button=key)
    #                 time.sleep(0.5 * mouse_duration)
    #             elif 'tapped' in line:
    #                 pyauto.click(button=key, x=coords[0], y=coords[1], duration=mouse_duration)
    #                 down = coords
    #             time.sleep(0.5)  # must be here to prevent some later operations from being cut off...
    #         elif 'scrolled.' in line:
    #             scroll_amnt = action.split(' at ')[0]
    #             if key == 'down':
    #                 pyauto.scroll(-60)
    #             elif key == 'up':
    #                 pyauto.scroll(60)
    #         elif 'key.' in line:
    #             if key == 'delete':
    #                 key = 'del'
    #             elif key == 'alt_l':
    #                 key = 'altleft'
    #             elif key == 'alt_r':
    #                 key = 'altright'
    #             elif key == 'cmd':
    #                 key = 'win'
    #             elif key == 'ctrl_l':
    #                 key = 'ctrlleft'
    #                 if 'tapped' in action:
    #                     try:
    #                         coords = coords_of(line)
    #                         pyauto.moveTo(x=coords[0], y=coords[1], duration=mouse_duration)
    #                     except IndexError:
    #                         pass
    #             elif key == 'page_up':
    #                 key = 'pageup'
    #             elif key == 'page_down':
    #                 key = 'pagedown'
    #             press(key, action)
    # else:
    #     if '```' in line:
    #         action = line.split('```')[1]
    #         key = line.split('```')[0]
    #         press(key, action)
    #     else:
    #         keys = line
    #         pyauto.typewrite(keys)

    print('\nComplete!')
    return


def output_to_file_bkup(output='', end='\n'):
    output = (output + end)
    with open('{}_bkup.txt'.format(workflow_name), 'a') as record_file:
        record_file.write(''.join(output))
    print(output, end='')
    return


def press(key, action):
    if 'pressed' in action:
        pyauto.keyDown(key)
    elif 'released' in action:
        pyauto.keyUp(key)
    elif 'tapped' in action:
        pyauto.press(key)
    return


def on_press_recording(key):
    global capslock
    global ctrls
    global recording
    output = str(key).strip('\'').lower()
    coords = ''
    if recording:
        if output == 'key.caps_lock':  # if capslock pressed, swap capslock state
            capslock = not capslock
        if output == 'key.space':  # if capslock pressed, swap capslock state
            output = ' '
        if output == 'key.ctrl_l':  # if left ctrl is pressed, record current mouse position
            coords = pyauto.position()
        if not output.startswith('key'):  # i.e., if output is alphanumeric
            if capslock:
                output = output.swapcase()
        if (output.startswith('\\') and output != '\\\\') or (output.startswith('<') and output.endswith('>')):
            output = 'ctrl+{}'.format(df['Translation'][output.replace('<', '').replace('>', '')])
        if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
            output_to_file_bkup('\\' + '```pressed')
            output = ''
        if output == '\"\'\"':
            output = '\''
        if (not output.startswith('key.ctrl_r')) and (
                not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
            if 'key' in output:
                output = '``' + output
            output = output + '```pressed'
            if coords:
                output = output + ' at {}'.format((coords[0], coords[1]))
            output_to_file_bkup(output)
    if 'key.ctrl_r' in output:
        ctrls += 1
        # if not recording:
        print('{}  '.format(ctrls), end='')
    if 'key.ctrl_r' in output and ctrls >= 3:  # toggle recording
        ctrls = 0
        recording = not recording
        print()
        print('RECORDING = {}'.format(recording))
        if not recording:
            print('Complete!')
            compile_recording()
            raise SystemExit()
    return


def on_release_recording(key):
    global capslock
    global ctrls
    global recording
    output = str(key).strip('\'').lower()
    coords = ''
    if recording:
        if output == 'key.caps_lock':  # if capslock pressed, swap capslock state
            capslock = not capslock
        if output == 'key.space':  # if capslock pressed, swap capslock state
            output = ' '
        if output == 'key.ctrl_l':  # if left ctrl is pressed, record current mouse position
            coords = pyauto.position()
        if not output.startswith('key'):  # i.e., if output is alphanumeric
            if capslock:
                output = output.swapcase()
        if (output.startswith('\\') and output != '\\\\') or (output.startswith('<') and output.endswith('>')):
            output = 'ctrl+{}'.format(df['Translation'][output.replace('<', '').replace('>', '')])
        if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
            output_to_file_bkup('\\' + '```released')
            output = ''
        if output == '\"\'\"':
            output = '\''
        if (not output.startswith('key.ctrl_r')) and (
                not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
            if 'key' in output:
                output = '``' + output
            output = output + '```released'
            if coords:
                output = output + ' at {}'.format((coords[0], coords[1]))
            output_to_file_bkup(output)
    return


def on_click_recording(x, y, button, pressed):
    if recording:
        output_to_file_bkup('``{}```{} at {}'.format(str(button).lower(), 'pressed' if pressed else 'released', (x, y)))
    return


def on_scroll_recording(x, y, dx, dy):
    if recording:
        output_to_file_bkup('``scrolled.{}```1 at {}'.format('down' if dy < 0 else 'up', (x, y)))
    return


def on_move_recording(x, y):
    # if recording:
    #     output_to_file_bkup('``moved```{}'.format((x, y)))
    return


def coords_of(line):
    coords = line.split('(')[1].replace(' ', '').replace(')', '').split(',')
    coords = (int(coords[0]), int(coords[1]))
    return coords


def compile_recording():
    bkup_file = '{}_bkup.txt'.format(workflow_name)
    with open(bkup_file, 'r') as record_file:
        lines = record_file.readlines()
    with open('{}.txt'.format(workflow_name), 'w') as record_file:
        for line in lines:
            record_file.write(line)
    processed_lines = []
    skip = False
    previous_normal_key_tap = False
    for index, line in enumerate(lines[:-1]):
        if not skip:
            # print(line.replace('\n', ''), end='')
            if lines[index].replace('pressed', '') == lines[index + 1].replace('released', ''):
                # print(' -------------- True')
                skip = True
                if line[0:2] == '``':  # special functions
                    key = line.split('```')[0].split('.')[1]
                    if previous_normal_key_tap:
                        new_line = '\n'
                    else:
                        new_line = ''
                    if 'ctrl_l' in key:
                        coords = coords_of(line)
                        processed_line = new_line + '``move to {}\n``time.sleep({})\n'.format((coords[0], coords[1]),
                                                                                              mouse_hover_duration)
                    else:
                        processed_line = new_line + lines[index].replace('pressed', 'tapped')
                    previous_normal_key_tap = False
                else:
                    key = line.split('```')[0]
                    # if lines[index + 1][0:2] == '``':  # next_
                    processed_line = key
                    previous_normal_key_tap = True
            else:
                if previous_normal_key_tap:
                    new_line = '\n'
                else:
                    new_line = ''
                processed_line = new_line + line
                previous_normal_key_tap = False
            processed_lines.append(processed_line)
            print(processed_line, end='')
        else:
            skip = False
    processed_lines.append('\n' + lines[-1])
    print()
    print()
    # look for triple clicks
    processed_lines_to_remove = []
    skip = 0
    for index, (tripleA, tripleB, tripleC) in enumerate(zip(processed_lines, processed_lines[1:], processed_lines[2:])):
        if skip:
            skip -= 1
        else:
            if '``button.left```tapped' in tripleA and tripleA == tripleB == tripleC:
                skip = 3 - 1  # number of clicks minus one
                processed_lines[index] = '``tripleclick at {}\n'.format(coords_of(tripleA))
                processed_lines_to_remove.append(index + 1)
                processed_lines_to_remove.append(index + 2)
                processed_lines[index + 1] = ''
                processed_lines[index + 2] = ''
    for index in processed_lines_to_remove[::-1]:
        processed_lines.pop(index)

    # look for double clicks
    processed_lines_to_remove = []
    skip = 0
    for index, (pairA, pairB) in enumerate(zip(processed_lines, processed_lines[1:])):
        if skip:
            skip -= 1
        else:
            if '``button.left```tapped' in pairA and pairA == pairB:
                skip = 2 - 1  # number of clicks minus one
                processed_lines[index] = '``doubleclick at {}\n'.format(coords_of(pairA))
                processed_lines_to_remove.append(index + 1)
                processed_lines[index + 1] = ''
    for index in processed_lines_to_remove[::-1]:
        processed_lines.pop(index)

    print(processed_lines)
    with open('{}.txt'.format(workflow_name), 'w') as record_file:
        for line in processed_lines:
            record_file.write(line)
    print('The workflow recording compilation was successful.')
    return


def display_help():
    print('This is the Help placeholder.')
    print()


ctrls = 0
running = False


def main():
    global pause
    global mouse_hover_duration
    # pause = 0.02
    pause = 4
    mouse_hover_duration = 0.5

    print('Welcome to the Automation Tool by Noah Baculi, 2020')
    print('Remember, at any time to stop an automation execution, move the mouse cursor to the very left upper corner '
          'to trigger the failsafe.')
    print('For further instructions, enter \'Help\'.')
    print()
    while True:
        try:
            action = str(input('Input \'Record\', \'Compile\', or \'Execute\' to select an option: ')).lower()
            if action in ['h', 'help']:
                display_help()
            elif action in ['r', 'record']:
                action_status = 'record'
                recording_warning = 'This will erase all contents in any files of the same name.'
                break
            elif action in ['c', 'compile']:
                action_status = 'compile'
                recording_warning = ''
                break
            elif action in ['e', 'execute']:
                action_status = 'execute'
                recording_warning = ''
                break
            else:
                raise IndexError
        except IndexError:
            print('\tInvalid input, please enter \'Help\', \'Record\', \'Compile\', or \'Execute\'')

    global workflow_name
    confirmation = '_'
    while confirmation not in ['', 'y', 'yes']:
        confirmation = '_'
        while True:
            workflow_name = input(
                'Enter the workflow name (do not enter \'_bkup\' filenames without full understanding of implications): ')
            if '\\' not in workflow_name and '.' not in workflow_name and workflow_name != '':
                break
            else:
                print('\tInvalid input, please enter workflow name without periods or slashes.')
        if workflow_name.lower() == 'help':
            display_help()
        else:
            while True:
                confirmation = input(
                    'The workflow name is \"{}\". {} Enter \'Yes\' to confirm (this create or overwrite any existing workflows with the same name) or \'No\' to re-enter: '.format(
                        workflow_name, recording_warning))
                if confirmation in ['', 'y', 'yes']:
                    break

    print('Primed to {} actions for Workflow \"{}\"...'.format(action_status, workflow_name))

    if action_status == 'execute':
        print('\tNavigate to start of workflow and then press the right CTRL three times: ', end='')
        with keyboard.Listener(on_press=on_press_execute) as listener:
            listener.join()
    elif action_status == 'record':
        print('\tNavigate to start of workflow and then press the right CTRL three times: ', end='')
        global recording
        with open('{}_bkup.txt'.format(workflow_name), 'w') as record_file:
            record_file.write('')
        recording = False
        with mouse.Listener(on_click=on_click_recording, on_scroll=on_scroll_recording,
                            on_move=on_move_recording) as listener:
            with keyboard.Listener(on_press=on_press_recording, on_release=on_release_recording) as listener:
                listener.join()
    elif action_status == 'compile':
        compile_recording()


if __name__ == "__main__":
    main()
