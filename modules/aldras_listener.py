"""Aldras module containing ListenerThread"""
import threading
import pandas as pd
from pynput import keyboard, mouse
import wx
import re
import pyautogui as pyauto
from ctypes import WinDLL


class ListenerThread(threading.Thread):
    def __init__(self, parent, listen_to_key=True, listen_to_mouse=True, record=False, debug=False):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self, daemon=True)
        self.parent = parent
        self.listen_to_key = listen_to_key
        self.listen_to_mouse = listen_to_mouse
        self.record = record
        self.debug = debug
        self.in_action = False
        if self.record:
            self.recording_lines = []
        try:
            if __name__ == '__main__':
                ctrl_keys_file = f'../data/ctrl_keys_ref.csv'
            else:
                ctrl_keys_file = f'{self.parent.parent.parent.software_info.data_directory}ctrl_keys_ref.csv'
            self.ctrl_keys_df = pd.read_csv(ctrl_keys_file, names=['Translation', 'Code'])  # reference for all ctrl hotkeys (registered as separate key)
            self.ctrl_keys_df = self.ctrl_keys_df.set_index('Code')
        except FileNotFoundError as _:
            print('FileNotFoundError: [Errno 2] File ctrl_keys_ref.csv does not exist: \'ctrl_keys_ref.csv\'')
            raise FileNotFoundError

    def run(self):
        """Run worker thread."""
        self.ctrls = 0

        def output_to_file_bkup(output='', end='\n'):
            """Print string and write to file."""

            # TODO function still needed?

            if self.record:
                self.recording_lines.append(output)
                if self.debug:
                    print(f'self.recording_lines: {self.recording_lines}')
                    pass

            # output = (output + end)
            # print(output)

            # Will add back when recording is enabled
            # with open(workflow_name+'_bkup.txt', 'a') as record_file:
            #     record_file.write(''.join(output))
            # print(output, end='')

        if self.listen_to_key:
            def process_keystroke(key, key_action):
                """
                Process keystroke press or release for keyboard listener for ListenerThread instances.

                key: parameter passed by pynput listener identifying the key
                key_pressed: parameter passed to determine if key pressed or released
                    True: key is pressed
                    False: key is released
                """
                output = str(key).strip('\'').lower()  # strip single quotes and lower

                if self.in_action:
                    if not output.startswith('key'):  # change case if output is alphanumeric and capslock is active
                        # get capslock status on windows
                        if WinDLL("User32.dll").GetKeyState(0x14):  # TODO test on other platforms
                            output = output.swapcase()

                    if (output.startswith('\\') and output != '\\\\') or (output.startswith('<') and output.endswith('>')):  # substituted ctrl+_key_ value
                        try:
                            output = self.ctrl_keys_df['Translation'][output.replace('<', '').replace('>', '')]
                        except KeyError:
                            output = 'UNKNOWN-HOTKEY'

                    # eliminate 'key.' and make substitutions for backslash (\), single quote ('), and right ctrl (should be replaced with left)
                    output = output.replace('key.', '').replace('\\\\', '\\').replace('\"\'\"', '\'')

                    output = f'Key {output} {key_action}'

                    if 'ctrl_l' in output:  # if left ctrl is pressed, add current mouse position
                        output = f'{output} at {tuple(pyauto.position())}'

                    output_to_file_bkup(output)

                # process right ctrls
                if key_action == 'press':
                    if 'ctrl_r' in output:
                        self.ctrls += 1
                        if self.debug:
                            print(f'ctrl_r {self.ctrls}  ', end='')

                        event_message = 'Error 693578!'
                        if not self.in_action:
                            if self.ctrls == 1:
                                event_message = 'Action in 3'
                            elif self.ctrls == 2:
                                event_message = 'Action in 3 2'
                            elif self.ctrls == 3:
                                event_message = 'Action'

                        elif self.in_action:
                            if self.ctrls == 1:
                                event_message = 'Stopping in 3'
                            elif self.ctrls == 2:
                                event_message = 'Stopping in 3 2'
                            elif self.ctrls == 3:
                                event_message = 'Completed!'

                        if __name__ != '__main__':
                            wx.PostEvent(self.parent, ResultEvent(event_message, self.parent.thread_event_id))

                        if self.ctrls >= 3:
                            self.ctrls = 0
                            self.in_action = not self.in_action  # toggle other keystroke recognition

            self.key_listener = keyboard.Listener(on_press=lambda key: process_keystroke(key, 'press'), on_release=lambda key: process_keystroke(key, 'release'))
            self.key_listener.start()

        if self.listen_to_mouse:
            def process_click(x, y, button, pressed):
                """Process click for mouse listener for ListenerThread instances."""
                if self.in_action:
                    button = str(button).replace('Button.', '').capitalize()
                    output_to_file_bkup(f'{button}-mouse {"press" if pressed else "release"} at {(x, y)}')

            self.mouse_listener = mouse.Listener(on_click=process_click)
            self.mouse_listener.start()

        if __name__ == '__main__':  # allows function to be tested by running module file as main
            try:
                self.key_listener.join()
            except NameError:
                pass

    def abort(self):
        """Abort worker thread."""
        # Method for use by main thread to signal an abort

        if self.listen_to_key:
            self.key_listener.stop()
        if self.listen_to_mouse:
            self.mouse_listener.stop()
        if self.record:
            return self.compile_recording()
        else:
            return

    def compile_recording(self):
        lines = self.recording_lines
        print(f'lines: {lines}')

        mouse_hover_duration = 0.5
        processed_lines = []
        skip = False
        break_code = '```8729164788```'
        register_hotkey = False
        pressed_keys = []
        symbol_chars = ['[', '@', '_', '!', '#', '$', '%', '^', '&', '*', '(', ')', '<', '>', '?', '/', '\\', '|', '}',
                        '{', '~', ':', ']']
        replacement_keys_ref = {
            'ctrl': ['ctrl_l', 'ctrl_r'],
            'alt': ['alt_gr', 'alt_l', 'alt_r'],
            'shift': ['shift_l', 'shift_r'],
            'cmd': ['cmd_l', 'cmd_r'],
        }
        for index, line in enumerate(lines[:-1]):  # loop through all lines except last one (should be release)
            if not skip:
                line = line.replace('shift_l', 'shift').replace('shift_r', 'shift')
                print(f'line: {line}')
                key = line.split(' ')[1]
                print(f'key: {key}')

                if not pressed_keys and lines[index].replace('press', '') == lines[index + 1].replace('release',
                                                                                                      ''):  # if line press is same as next line release
                    print('ONLY TAP')

                    skip = True  # skip the next (release) line
                    if len(key) > 1:  # special functions

                        if 'ctrl_l' in line:  # if left ctrl is in line signalling mouse-move
                            coords = coords_of(line)
                            line = f'Mouse-move to {coords}{break_code}Wait {mouse_hover_duration}{break_code}'
                        elif key == 'space':
                            line = 'Type: '

                        else:
                            if 'mouse' in line:
                                tap_replacement = 'click'
                            else:
                                tap_replacement = 'tap'
                            line = lines[index].replace('press', tap_replacement)

                        processed_line = f'{break_code}{line}{break_code}'

                    else:  # alphanumeric keys (try to compile into type command)
                        processed_line = f'{break_code}Type:{key}{break_code}'

                else:  # line press not equal to next line release
                    print(f'NOT TAP: {line}')
                    if 'Key' in line:
                        if 'press' in line:
                            if index != len(lines) - 1:
                                pressed_keys.append(key)
                                pressed_keys = eliminate_duplicates(pressed_keys)
                                register_hotkey = True
                                line = ''

                        if 'release' in line and key in pressed_keys:
                            # execute hotkey
                            if register_hotkey:
                                check_single_chars = {len(x) for x in pressed_keys if x != 'shift'} == {
                                    1}  # all hotkeys are single chars
                                check_alphabet_letters = {x.isalpha() for x in pressed_keys if x != 'shift'} == {
                                    True}  # all hotkeys are alphabet
                                check_symbol_chars = {x for x in pressed_keys if
                                                      x in symbol_chars}  # any hotkeys are symbols
                                if 'shift' in pressed_keys and check_single_chars and (
                                        check_alphabet_letters or check_symbol_chars):
                                    line = f"Type:{''.join([x.capitalize() for x in pressed_keys if x != 'shift'])}"
                                    # pressed_keys = []
                                else:
                                    line = f"Hotkey {' + '.join(pressed_keys)}"
                            else:
                                line = ''
                            register_hotkey = False
                            if key in pressed_keys:
                                pressed_keys.remove(key)

                        print(f'pressed_keys: {pressed_keys}')

                    # else:
                    if line:
                        processed_line = f'{break_code}{line}{break_code}'
                    else:
                        processed_line = ''

                for master_key, replacement_keys in replacement_keys_ref.items():
                    for replacement_key in replacement_keys:
                        processed_line = processed_line.replace(replacement_key, master_key)

                processed_lines.append(processed_line)
                print(f'processed_line: {processed_line}')
            else:
                skip = False

            print()
        # processed_lines.append(break_code + lines[-1])
        print(processed_lines)
        processed_lines = ''.join(processed_lines).split(break_code)
        processed_lines = [x for x in processed_lines if x]
        print()
        print()

        # consolidate triple clicks
        processed_lines_to_remove = []
        skip = 0
        for index, (tripleA, tripleB, tripleC) in enumerate(
                zip(processed_lines, processed_lines[1:], processed_lines[2:])):
            if skip:
                skip -= 1
            else:
                if 'Left-mouse click' in tripleA and tripleA == tripleB == tripleC:
                    skip = 3 - 1  # number of clicks minus one
                    processed_lines[index] = f'Triple-click at {coords_of(tripleA)}\n'
                    processed_lines_to_remove.append(index + 1)
                    processed_lines_to_remove.append(index + 2)
                    processed_lines[index + 1] = ''
                    processed_lines[index + 2] = ''
        for index in processed_lines_to_remove[::-1]:
            processed_lines.pop(index)

        # consolidate double clicks
        processed_lines_to_remove = []
        skip = 0
        for index, (pairA, pairB) in enumerate(zip(processed_lines, processed_lines[1:])):
            if skip:
                skip -= 1
            else:
                if 'Left-mouse click' in pairA and pairA == pairB:
                    skip = 2 - 1  # number of clicks minus one
                    processed_lines[index] = f'Double-click at {coords_of(pairA)}\n'
                    processed_lines_to_remove.append(index + 1)
                    processed_lines[index + 1] = ''
        for index in processed_lines_to_remove[::-1]:
            processed_lines.pop(index)

        print(processed_lines)

        # consolidate consecutive type commands
        def consecutive_ranges_of(list_in):
            """Returns consecutive ranges of integers in list."""
            nums = sorted(set(list_in))
            gaps = [[start, end] for start, end in zip(nums, nums[1:]) if start + 1 < end]
            edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
            return list(zip(edges, edges))

        typing_indices = [index for index, line in enumerate(processed_lines) if 'Type:' in line]
        typing_ranges = consecutive_ranges_of(typing_indices)
        print(list(reversed(typing_ranges)))
        for typing_range in reversed(typing_ranges):
            if typing_range[0] != typing_range[1]:  # only if range is not a single index
                consolidated_type = ''
                for index in reversed(range(typing_range[0], typing_range[1] + 1)):
                    line = processed_lines[index]
                    consolidated_type = f"{re.compile(re.escape('type:'), re.IGNORECASE).sub('', line)}{consolidated_type}"
                    if index != typing_range[0]:
                        del processed_lines[index]
                processed_lines[typing_range[0]] = f'Type:{consolidated_type}'

        print(processed_lines)
        return processed_lines


class ResultEvent(wx.PyEvent):
    """Event to carry result data."""

    def __init__(self, data, event_id):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(int(event_id))
        self.data = data


def coords_of(line):
    """Returns tuple of parsed coordinates from string."""

    try:
        x_coord = re.findall(r'\d+', re.findall(r'(?<=\()(.*?)(?=,)', line)[0])[0]  # find first integer between '(' and','
    except IndexError:
        x_coord = 0
    try:
        y_coord = re.findall(r'\d+', re.findall(r'(?<=,)(.*?)(?=\))', line)[0])[0]  # find first integer between ',' and')'
    except IndexError:
        y_coord = 0

    return x_coord, y_coord


def eliminate_duplicates(list_with_duplicates):
    """Eliminates duplicates from list"""
    seen = set()
    return [x for x in list_with_duplicates if not (x in seen or seen.add(x))]


if __name__ == '__main__':  # debugging capability by running module file as main
    wx.DisableAsserts()  # disable alerts of non functioning wx.PostEvent
    listener_thread = ListenerThread(None, wx.NewIdRef(), record=True, debug=True)
    listener_thread.start()
    listener_thread.join()

