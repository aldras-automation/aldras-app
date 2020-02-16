from pynput import keyboard
from pynput import mouse
import pandas as pd
from time import sleep

file_name = 'test_pract'
capslock = False
ctrls = 0
recording = False
previous_base_key = False

df = pd.read_csv('ctrl_keys_ref.csv', names=['Translation', 'Code'])
df = df.set_index('Code')
# print(df)


def clear_file():
    with open('{}.txt'.format(file_name), 'w') as record_file:
        record_file.write('')


def output_to_file(output='', end='\n'):
    output = output + end
    with open('{}.txt'.format(file_name), 'a') as record_file:
        record_file.write(''.join(output))
    print(output, end='')


def on_press(key):
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
        # print(ctrls)
    if 'Key.ctrl_r' in output and ctrls >= 3:  # toggle recording
        ctrls = 0
        recording = not recording
        if previous_base_key:
            print()
        print('RECORDING = {}'.format(recording))


def on_click(x, y, button, pressed):
    if recording:
        if pressed:
            if previous_base_key:
                output_to_file()
            output_to_file('`````{} {} at ({}, {})'.format(button, 'Pressed' if pressed else 'Released', x, y))


def on_scroll(x, y, dx, dy):
    if recording:
        if previous_base_key:
            output_to_file()
        output_to_file('`````Scrolled {} at {}'.format('down' if dy < 0 else 'up', (x, y)))
    return


def on_move(x, y):
    # if recording:
    #     if previous_base_key:
    #         output_to_file()
    #     output_to_file('`````Moved to {}'.format((x, y)))
    return


def main():
    clear_file()
    with mouse.Listener(on_click=on_click, on_scroll=on_scroll, on_move=on_move) as listener:
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()


if __name__ == "__main__":
    main()
