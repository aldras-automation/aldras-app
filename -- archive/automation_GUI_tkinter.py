import math
import threading
import tkinter as tk
from time import sleep

import pandas as pd
import pyautogui as pyauto
from PIL import ImageTk, Image
from pynput import keyboard, mouse


# failsafe - mouse cursor to top left corner

# TODO ctrl key calibration setup
# TODO re-runs
# TODO comments
# TODO allow workflow comments
# TODO create help guide
# TODO allow multiple rerun executions (loops)
# TODO names and domain
# TODO icon
# TODO classes


def on_press_execute(key):
    global ctrls
    global running

    output = str(key).strip('\'')
    if 'Key.ctrl_r' in output:
        ctrls += 1
        output_to_gui('{}  '.format(ctrls), end='')
    if 'Key.ctrl_r' in output and ctrls >= 3:  # toggle running
        ctrls = 0
        running = True
        output_to_gui()
        output_to_gui('\tExecuting')
        execute()
    return


def execute():
    pyauto.PAUSE = pause
    with open('{}.txt'.format(workflow_name), 'r') as record_file:
        lines = record_file.readlines()
    for line in lines:
        # sleep(0.5)
        line = line.replace('\n', '').lower()
        output_to_gui(line)

        if line[0:2] == '``':  # special functions
            if '#' in line:  # workflow comment so no action
                pass
            elif 'sleep' in line:
                sleep(float(line.replace('``sleep(', '').replace(')', '')))
            elif 'doubleclick' in line:
                coords = coords_of(line)
                pyauto.click(clicks=2, x=coords[0], y=coords[1], duration=mouse_duration)
            elif 'tripleclick' in line:
                coords = coords_of(line)
                pyauto.click(clicks=3, x=coords[0], y=coords[1], duration=mouse_duration)
            elif 'move' in line:
                coords = coords_of(line)
                pyauto.moveTo(x=coords[0], y=coords[1], duration=mouse_duration)
            else:
                action = line.split('```')[1]
                key = line.split('```')[0].split('.')[1]
                if 'button.' in line:
                    coords = line.split('(')[-1].replace(')', '').replace(' ', '').split(',')
                    coords[0] = int(coords[0])
                    coords[1] = int(coords[1])
                    if 'press' in line:
                        pyauto.mouseDown(button=key, x=coords[0], y=coords[1])
                        down = coords
                    elif 'release' in line:
                        # pyauto.mouseUp(button='left', x=int(coords[0]), y=int(coords[1]), duration=drag_duration)
                        drag_dist = math.hypot(down[0] - coords[0], down[1] - coords[1])
                        drag_duration = 0.5 * mouse_duration + (drag_dist / drag_duration_scale)
                        pyauto.moveTo(x=coords[0], y=coords[1], duration=drag_duration)
                        pyauto.mouseUp(button=key)
                        sleep(0.5 * mouse_duration)
                    elif 'tapped' in line:
                        pyauto.click(button=key, x=coords[0], y=coords[1], duration=mouse_duration)
                        down = coords
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
                        if 'tapped' in action:
                            try:
                                coords = coords_of(line)
                                pyauto.moveTo(x=coords[0], y=coords[1], duration=mouse_duration)
                            except IndexError:
                                pass
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

    output_to_gui('\nComplete!')
    return


def output_to_gui(output='', end='\n'):
    global main_text
    print(output)
    output = (output + end)
    main_text.insert(tk.END, output)
    return


def output_to_file_bkup(output='', end='\n'):
    output = (output + end)
    with open('{}_bkup.txt'.format(workflow_name), 'a') as record_file:
        record_file.write(''.join(output))
    output_to_gui(output, end='')
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
    global recording_control
    output = str(key).strip('\'').lower()
    coords = ''
    if recording_control:
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
            output = '{}'.format(df['Translation'][output.replace('<', '').replace('>', '')])
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
        if not recording_control:
            output_to_gui('{}  '.format(ctrls), end='')
    if 'key.ctrl_r' in output and ctrls >= 3:  # toggle recording
        ctrls = 0
        recording_control = not recording_control
        output_to_gui()
        output_to_gui('RECORDING = {}'.format(recording_control))
        if not recording_control:
            output_to_gui('Complete!')
            compile_recording()
            raise SystemExit()
    return


def on_press_release(key):
    global capslock
    global ctrls
    global recording_control
    output = str(key).strip('\'').lower()
    coords = ''
    if recording_control:
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
    if recording_control:
        output_to_file_bkup('``{}```{} at {}'.format(str(button).lower(), 'pressed' if pressed else 'released', (x, y)))
    return


def on_scroll_recording(x, y, dx, dy):
    if recording_control:
        output_to_file_bkup('``scrolled.{}```1 at {}'.format('down' if dy < 0 else 'up', (x, y)))
    return


def on_move_recording(x, y):
    # if recording_control:
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
            # output_to_GUI(line.replace('\n', ''), end='')
            if lines[index].replace('pressed', '') == lines[index + 1].replace('released', ''):
                # output_to_GUI(' -------------- True')
                skip = True
                if line[0:2] == '``':  # special functions
                    key = line.split('```')[0].split('.')[1]
                    if previous_normal_key_tap:
                        new_line = '\n'
                    else:
                        new_line = ''
                    if 'ctrl_l' in key:
                        coords = coords_of(line)
                        processed_line = new_line + '``move to {}\n``sleep({})\n'.format((coords[0], coords[1]),
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
            output_to_gui(processed_line, end='')
        else:
            skip = False
    processed_lines.append('\n' + lines[-1])
    output_to_gui()
    output_to_gui()
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

    output_to_gui(processed_lines)
    with open('{}.txt'.format(workflow_name), 'w') as record_file:
        for line in processed_lines:
            record_file.write(line)
    output_to_gui('The workflow recording compilation was successful.')
    return


def display_help():
    output_to_gui('This is the Help placeholder.')
    output_to_gui()
    return


def scan():
    with open('{}.txt'.format(file_name), 'r') as record_file:
        lines = record_file.readlines()
    pyauto.PAUSE = 0.5
    for line in lines:
        sleep(0.5)
        line = line.replace('\n', '')
        output_to_gui(line)
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

    output_to_gui('\nComplete!')
    return


def empty_workflow_name_error():
    popup = tk.Tk()
    popup.iconbitmap('logo.ico')
    popup.wm_title("Invalid Workflow Name")
    popup.geometry('300x100')
    # container = tk.Frame(popup)
    # container.grid(row=0, column=0, padx=(100, 100), pady=(20, 20))
    label = tk.Label(popup, text='The workflow name cannot be blank.')
    label.pack(side="top", fill="x", pady=10)
    B1 = tk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()
    return


def record(workflow_name_in):
    # await_trigger()
    global in_action
    global workflow_name
    global recording_control
    global record_text
    workflow_name = workflow_name_in

    if workflow_name == '':
        empty_workflow_name_error()
        return

    recording = not recording
    if recording:
        record_text.set('Stop Recording')
        with open('{}_bkup.txt'.format(workflow_name), 'w') as record_file:
            record_file.write('')
        record_button.configure(background='red')
        output_to_gui('Primed for recording. To start recording, press the right CTRL three times.')
    else:
        record_text.set('Record')
        record_button.configure(background='SystemButtonFace')
        output_to_gui('Recording complete.')
    recording_control = False
    # output_to_GUI(workflow_name)
    return


def workflow_selection(main_frame, workflow_name_in):
    global workflow_name
    workflow_name = workflow_name_in
    if workflow_name == '':
        empty_workflow_name_error()
        return
    main_frame.tkraise()


def gui_thread(num):
    global workflow_name
    global workflow_name_entry
    global record_button
    global m
    global main_text
    global record_text
    m = tk.Tk()
    m.title('Automation Tool')
    m.iconbitmap('logo.ico')
    m.configure(bg='white')

    container = tk.Frame(m)
    container.grid(row=0, column=0, padx=(100, 100), pady=(20, 20))

    workflow_id_frame = tk.Frame(container, bg='white')
    main_frame = tk.Frame(container, bg='white')

    for frame in (workflow_id_frame, main_frame):
        frame.grid(row=0, column=0, sticky='news')

    workflow_id_frame.tkraise()
    logo_img = ImageTk.PhotoImage(Image.open('logo.png').resize((150, 150)))
    logo_img_label = tk.Label(workflow_id_frame, bg='white', image=logo_img)
    logo_img_label.grid(row=0, column=0, columnspan=4)
    m.grid_rowconfigure(0, weight=1)
    m.grid_columnconfigure(0, weight=1)
    program_name = tk.Label(workflow_id_frame, bg='white', text='Aldras Automation')
    program_name.config(font=('Verdana', 16))
    program_name.grid(row=1, column=0, columnspan=4, pady=(0, 20))
    tk.Label(workflow_id_frame, bg='white', text='Workflow:').grid(row=2, column=1)
    workflow_name_entry = tk.Entry(workflow_id_frame, relief=tk.FLAT, highlightbackground='blue', highlightcolor='blue',
                                   highlightthickness=1)
    workflow_name_entry.grid(row=2, column=2)
    tk.Label(workflow_id_frame, bg='white', text='', width=6).grid(row=2, column=3)

    recent_workflows = False
    if recent_workflows:
        # do stuff to allow quick selection of recent workflows
        ok_row = 5
    else:
        ok_row = 4

    workflow_id_frame.grid_rowconfigure(ok_row - 1, minsize=20)
    button_frame = tk.Frame(workflow_id_frame)
    button_frame.grid(row=ok_row, column=2, columnspan=2, sticky=tk.E)
    tk.Button(button_frame, text='Quit', width=8, command=m.destroy).grid(row=0, column=0)
    tk.Button(button_frame, text='OK', width=8,
              command=lambda: workflow_selection(main_frame, workflow_name_entry.get())).grid(row=0, column=1)

    m.mainloop()
    raise SystemExit()

    record_text = tk.StringVar()
    record_button = tk.Button(m, textvariable=record_text, width=25, command=lambda: record(workflow_name_entry.get()))
    record_text.set('Record')
    record_button.grid(row=1, column=1)
    m.grid_columnconfigure(1, weight=1)
    tk.Label(m, text='', width=10).grid(row=1, column=2)

    tk.Label(m, text='', width=10).grid(row=1, column=5)
    tk.Button(m, text='Execute', width=25, command=lambda: execute(workflow_name_entry.get())).grid(row=1, column=6)
    m.grid_columnconfigure(6, weight=1)

    # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    main_text = tk.Text(m)
    main_text.grid(row=2, column=1, columnspan=6)
    scrollbar = tk.Scrollbar(m)
    scrollbar.config(command=main_text.yview)
    scrollbar.grid(row=2, column=7, sticky='nsew')
    main_text['yscrollcommand'] = scrollbar.set
    tk.Button(m, text='Quit', width=25, command=m.destroy).grid(row=3, column=6)
    m.bind('<Return>', execute)
    m.grid_rowconfigure(3, weight=1)

    return

    # sys.exit()


def listener_thread(num):
    while True:
        if in_action:
            global recording_control
            recording_control = False
            with mouse.Listener(on_click=on_click_recording, on_scroll=on_scroll_recording,
                                on_move=on_move_recording) as listener:
                with keyboard.Listener(on_press=on_press_recording, on_release=on_press_release) as listener:
                    listener.join()


# def execute(workflow_name_entry):
#     output_to_GUI('Workflow: {}'.format(workflow_name_entry))
#     workflow_name.set(workflow_name_entry)
#     main_text.delete('1.0', tk.END)
#     main_text.insert(tk.END, 'Workflow: {}'.format(workflow_name_entry))
#     pass

df = pd.read_csv('ctrl_keys_ref.csv', names=['Translation', 'Code'])
df = df.set_index('Code')
capslock = False
ctrls = 0
drag_duration_scale = math.hypot(pyauto.size().width, pyauto.size().width)
running = False
in_action = False
file_name = 'automation1'
pause = 0.5
mouse_duration = 0.2
mouse_hover_duration = 0.5

if __name__ == '__main__':
    t1 = threading.Thread(target=gui_thread, args=(10,))
    t2 = threading.Thread(target=listener_thread, args=(10,), daemon=True)
    t1.start()
    t2.start()
    # t1.join()
    # t2.join()
