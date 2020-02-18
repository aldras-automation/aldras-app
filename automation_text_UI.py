import pyautogui as pyauto
from pynput import keyboard, mouse
from time import sleep
import pandas as pd
import math
# failsafe - mouse cursor to top left corner
# TODO allow 'yes' or 'y' for responses
# TODO right-click recording and execution
# TODO ctrl key calibration setup
# TODO re-runs
# TODO comments
# TODO allow workflow comments
# TODO GUI

df = pd.read_csv('ctrl_keys_ref.csv', names=['Translation', 'Code'])
df = df.set_index('Code')
capslock = False
ctrls = 0
drag_duration_scale = math.hypot(pyauto.size().width, pyauto.size().width)


def press(key, action):
    if action == 'pressed':
        pyauto.keyDown(key)
    elif action == 'released':
        pyauto.keyUp(key)
    elif action == 'tapped':
        pyauto.press(key)
        print('\t{} actually tapped'.format(key))
    return


def execute():
    pyauto.PAUSE = pause
    with open('{}.txt'.format(workflow_name), 'r') as record_file:
        lines = record_file.readlines()
    for line in lines:
        # sleep(0.5)
        line = line.replace('\n', '').lower()
        print(line)

        if line[0:2] == '``':  # special functions
            action = line.split('```')[1]
            if '```sleep' in line:
                sleep(float(line.replace('```sleep(', '').replace(')', '')))
            else:
                key = line.split('```')[0].split('.')[1]
                if 'button.left' in line:
                    coords = line.split('(')[-1].replace(')', '').replace(' ', '').split(',')
                    coords[0] = int(coords[0])
                    coords[1] = int(coords[1])
                    if 'press' in line:
                        pyauto.mouseDown(button='left', x=coords[0], y=coords[1])
                        down = coords
                    elif 'release' in line:
                        # pyauto.mouseUp(button='left', x=int(coords[0]), y=int(coords[1]), duration=drag_duration)
                        drag_dist = math.hypot(down[0] - coords[0], down[1] - coords[1])
                        drag_duration = mouse_duration + (drag_dist / drag_duration_scale)
                        pyauto.moveTo(x=coords[0], y=coords[1], duration=drag_duration)
                        pyauto.mouseUp()
                    elif 'tapped' in line:
                        pyauto.click(x=coords[0], y=coords[1], duration=mouse_duration)
                    sleep(0.5)  # must be here to prevent some later operations from being cut off...
                elif 'scrolled.' in line:
                    scroll_amnt = action.split(' at ')[0]
                    if key == 'down':
                        pyauto.scroll(-60)
                    elif key == 'up':
                        pyauto.scroll(60)
                elif 'key.' in line:
                    if key == 'delete':
                        key = 'del'
                    elif key == 'alt_l':
                        key = 'altleft'
                    elif key == 'alt_r':
                        key = 'altright'
                    elif key == 'cmd':
                        key = 'win'
                    elif key == 'ctrl_l':
                        key = 'ctrlleft'
                    elif key == 'page_up':
                        key = 'pageup'
                    elif key == 'page_down':
                        key = 'pagedown'
                    press(key, action)
        else:
            if '```' in line:
                action = line.split('```')[1]
                key = line.split('```')[0]
                press(key, action)
            else:
                keys = line
                pyauto.typewrite(keys)

    print('\nComplete!')
    return


def clear_file_bkup():
    with open('{}_bkup.txt'.format(workflow_name), 'w') as record_file:
        record_file.write('')
    return


def output_to_file_bkup(output='', end='\n'):
    output = (output + end)
    with open('{}_bkup.txt'.format(workflow_name), 'a') as record_file:
        record_file.write(''.join(output))
    print(output, end='')
    return


def on_press_recording(key):
    global capslock
    global ctrls
    global recording
    output = str(key).strip('\'').lower()
    if recording:
        if output == 'key.caps_lock':  # if capslock pressed, swap capslock state
            capslock = not capslock
        if output == 'key.space':  # if capslock pressed, swap capslock state
            output = ' '
        if not output.startswith('key'):  # i.e., if output is alphanumeric
            if capslock:
                output = output.swapcase()
        if (output.startswith('\\') and output != '\\\\') or (output.startswith('<') and output.endswith('>')):
            output = '{}'.format(df['Translation'][output.replace('<', '').replace('>', '')])
        if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
            output_to_file_bkup('\\'+'```pressed')
            output = ''
        if output == '\"\'\"':
            output = '\''
        if (not output.startswith('key.ctrl_r')) and (not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
            if 'key' in output:
                output = '``' + output
            output_to_file_bkup(output + '```pressed')
    if 'key.ctrl_r' in output:
        ctrls += 1
        if not recording:
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


def on_press_release(key):
    global capslock
    global ctrls
    global recording
    output = str(key).strip('\'').lower()
    if recording:
        if output == 'key.caps_lock':  # if capslock pressed, swap capslock state
            capslock = not capslock
        if output == 'key.space':  # if capslock pressed, swap capslock state
            output = ' '
        if not output.startswith('key'):  # i.e., if output is alphanumeric
            if capslock:
                output = output.swapcase()
        if (output.startswith('\\') and output != '\\\\') or (output.startswith('<') and output.endswith('>')):
            output = 'ctrl+{}'.format(df['Translation'][output.replace('<', '').replace('>', '')])
        if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
            output_to_file_bkup('\\'+'```released')
            output = ''
        if output == '\"\'\"':
            output = '\''
        if (not output.startswith('key.ctrl_r')) and (not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
            if 'key' in output:
                output = '``' + output
            output_to_file_bkup(output + '```released')
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
            if lines[index].replace('pressed', '') == lines[index+1].replace('released', ''):
                # print(' -------------- True')
                skip = True
                if line[0:2] == '``':  # special functions
                    key = line.split('```')[0].split('.')[1]
                    if previous_normal_key_tap:
                        new_line = '\n'
                    else:
                        new_line = ''
                    processed_line = new_line + lines[index].replace('pressed', 'tapped')
                    # processed_line = '\n\n\n\n\n\n' + lines[index].replace('pressed', 'tapped')
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
    global mouse_duration
    # pause = 0.02
    pause = 0.5
    mouse_duration = 0

    print('Welcome to the Automation Tool by Noah Baculi, 2020')
    print('Remember, at any time to stop an automation execution, move the mouse cursor to the very left upper corner '
          'to trigger the failsafe.')
    print('For further instructions, enter \'Help\'.')
    print()
    while True:
        action = str(input('Input \'Record\', \'Compile\', or \'Execute\' to select an option: '))[0]
        if action == 'h':
            display_help()
        elif action != 'r' and action != 'c' and action != 'e':
            print('\tInvalid input, please enter \'Help\', \'Record\', \'Compile\', or \'Execute\'')
        elif action == 'r':
            action_status = 'record'
            recording_warning = 'This will erase all contents in any files of the same name.'
            break
        elif action == 'c':
            action_status = 'compile'
            recording_warning = ''
            break
        elif action == 'e':
            action_status = 'execute'
            recording_warning = ''
            break

    global workflow_name
    confirmation = '_'
    while confirmation not in ['', 'y']:
        confirmation = '_'
        while True:
            workflow_name = input('Enter the workflow name (do not enter \'_bkup\' filenames without full understanding of implications): ')
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

    if action == 'e':
        print('\tNavigate to start of workflow and then press the right CTRL three times: ', end='')
        with keyboard.Listener(on_press=on_press_execute) as listener:
            listener.join()
    elif action == 'r':
        print('\tNavigate to start of workflow and then press the right CTRL three times: ', end='')
        global recording
        clear_file_bkup()
        recording = False
        with mouse.Listener(on_click=on_click_recording, on_scroll=on_scroll_recording, on_move=on_move_recording) as listener:
            with keyboard.Listener(on_press=on_press_recording, on_release=on_press_release) as listener:
                listener.join()
    elif action == 'c':
        compile_recording()


if __name__ == "__main__":
    main()
