"""Aldras module containing listener and execute thread objects"""
import threading
import pandas as pd
from pynput import keyboard, mouse
import wx
import re
import pyautogui as pyauto
from ctypes import WinDLL
import math
import time
from modules.aldras_core import coords_of, eliminate_duplicates, float_in, variable_names_in, \
    assignment_variable_value_in, conditional_operation_in, conditional_comparison_in, block_end_index


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
        self.record_pause = None  # no pauses default
        if self.record:
            self.recording_lines = []
        try:
            if __name__ == '__main__':
                ctrl_keys_file = f'../data/ctrl_keys_ref.csv'
            else:
                ctrl_keys_file = f'{self.parent.parent.parent.software_info.data_directory}ctrl_keys_ref.csv'
            self.ctrl_keys_df = pd.read_csv(ctrl_keys_file, names=['Translation',
                                                                   'Code'])  # reference for all ctrl hotkeys (registered as separate key)
            self.ctrl_keys_df = self.ctrl_keys_df.set_index('Code')
        except FileNotFoundError as _:
            print('FileNotFoundError: [Errno 2] File ctrl_keys_ref.csv does not exist: \'ctrl_keys_ref.csv\'')
            raise FileNotFoundError

    def run(self):
        """Run worker thread."""
        self.ctrls = 0
        self.time_last_input = None

        def save_command(output=''):
            """Save recording line."""

            if self.record:
                if self.parent.Name == 'record_counter_dialog':
                    if self.parent.FindWindowByName('All pauses over 0.5').GetValue():
                        self.record_pause = 0.5
                    elif self.parent.FindWindowByName('Pauses over').GetValue():
                        self.record_pause = float_in(self.parent.FindWindowByName('some_sleep_thresh').GetValue())
                        if self.record_pause < 0.5:
                            self.record_pause = 0.5

                if self.record_pause:
                    # add pause since last input
                    if self.time_last_input:
                        record_interval = round(time.time() - self.time_last_input, 2)
                        if record_interval > self.record_pause:  # only consider pauses longer than pause parameter
                            self.recording_lines.append(f'Wait {record_interval}')

                self.recording_lines.append(output)

                self.time_last_input = time.time()

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
                    # replace numberpad virtual keycodes with strings of the number digits
                    for number in range(10):  # loop through 0-9 and replace keycodes starting at <96>
                        key = str(key).replace(f'<{96 + number}>', str(number))

                    # replace numberpad period with string
                    key = str(key).replace('<110>', '.')

                    output = str(key).strip('\'').lower()  # strip single quotes and lower

                    if not output.startswith('key'):  # change case if output is alphanumeric and capslock is active
                        # get capslock status on windows
                        if WinDLL("User32.dll").GetKeyState(0x14):  # TODO test on other platforms
                            output = output.swapcase()

                    if (output.startswith('\\') and output != '\\\\') or (
                            output.startswith('<') and output.endswith('>')):  # substituted ctrl+_key_ value
                        try:
                            output = self.ctrl_keys_df['Translation'][output.replace('<', '').replace('>', '')]
                        except KeyError:
                            output = 'UNKNOWN-HOTKEY'

                    # eliminate 'key.' and make substitutions for backslash (\), single quote ('), and right ctrl (should be replaced with left)
                    output = output.replace('key.', '').replace('\\\\', '\\').replace('\"\'\"', '\'')

                    output = f'Key {output} {key_action}'

                    if 'ctrl_l' in output:  # if left ctrl is pressed, add current mouse position
                        output = f'{output} at {tuple(pyauto.position())}'

                    if 'ctrl_r' not in output:  # ignore right ctrl trigger keystrokes
                        save_command(output)

                # process right ctrls
                if key_action == 'press':
                    if 'ctrl_r' in output:
                        self.ctrls += 1
                        if self.debug:
                            print(f'ctrl_r {self.ctrls}  ', end='')
                            if self.ctrls == 3:
                                print()

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

                            if __name__ == '__main__' and not self.in_action:
                                self.abort()

            self.key_listener = keyboard.Listener(on_press=lambda key: process_keystroke(key, 'press'),
                                                  on_release=lambda key: process_keystroke(key, 'release'))
            self.key_listener.start()

        if self.listen_to_mouse:
            def process_click(x, y, button, pressed):
                """Process click for mouse listener for ListenerThread instances."""
                if self.in_action:
                    button = str(button).replace('Button.', '').capitalize()
                    save_command(f'{button}-mouse {"press" if pressed else "release"} at {(x, y)}')

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
        if self.debug:
            print(f'\nCOMPILING RECORDING LINES {50 * "-"}\n')
            print(f'lines: {lines}\n')

        mouse_hover_duration = 0.5
        processed_lines = []
        skip = False
        break_code = '```8729164788```'
        pressed_keys = []
        symbol_chars = ['[', '@', '_', '!', '#', '$', '%', '^', '&', '*', '(', ')', '<', '>', '?', '/', '\\', '|', '}',
                        '{', '~', ':', ']']
        replacement_keys_ref = {
            'ctrl': ['ctrl_l', 'ctrl_r'],
            'alt': ['alt_gr', 'alt_l', 'alt_r'],
            'shift': ['shift_l', 'shift_r'],
            'win': ['cmd_l', 'cmd_r', 'cmd'],

            # translations from pynput commands to Aldras (PyAutoGui) commands
            'pageup': ['page_up'],
            'pagedown': ['page_down'],
            'del': ['delete'],
            'prntscrn': ['print_screen'],
            'scrolllock': ['scroll_lock'],
            'playpause': ['media_play_pause'],
            'nexttrack': ['media_next'],
            'prevtrack': ['media_previous'],
            'volumemute ': ['media_volume_mute'],
            'volumedown ': ['media_volume_down'],
            'volumeup ': ['media_volume_up'],
        }
        # # manual lines example for testing
        # lines = ['Key ctrl_l press at (2681, 64)', 'Key ctrl_l release at (2681, 69)']
        for index, line in enumerate(lines):  # loop through all lines
            if not skip:
                line = line.replace('shift_l', 'shift').replace('shift_r', 'shift')
                key = line.split(' ')[1]
                if self.debug:
                    print(f'\tline: {line}')
                    print(f'\tkey: {key}')

                # determine if the line indicates a tap if the next line matches (must catch last line since there is not line after the last line)
                only_tap = False
                try:
                    only_tap = lines[index].replace('press', '') == lines[index + 1].replace('release', '')

                    # if not yet tap and the first 10 characters match and there are brackets in the line
                    if not only_tap and lines[index].replace('press', '')[:12] == lines[index + 1].replace('release',
                                                                                                           '')[
                                                                                  :12] and '(' in line and ')' in line:
                        press_coord = coords_of(line)
                        release_coord = coords_of(lines[index + 1])
                        distance = abs(abs(press_coord[0] - release_coord[0]) + abs(press_coord[1] - release_coord[1]))

                        if distance <= 10:  # process commands with low distance as only taps
                            only_tap = True

                except IndexError:
                    pass

                if not pressed_keys and only_tap:  # if line press is same as next line release
                    if self.debug:
                        print('\tONLY TAP')

                    skip = True  # skip the next (release) line
                    if len(key) > 1:  # special functions

                        if 'ctrl_l' in line:  # if left ctrl is in line indicating mouse-move
                            coords = coords_of(line)
                            line = f'Mouse-move to {coords}{break_code}Wait {mouse_hover_duration}{break_code}'
                        elif key == 'space':
                            line = 'Type: '

                        else:
                            if 'mouse' in line:
                                press_replacement = 'click'
                            else:
                                press_replacement = 'tap'
                            line = lines[index].replace('press', press_replacement)

                        processed_line = f'{break_code}{line}{break_code}'

                    else:  # alphanumeric keys (try to compile into type command)
                        processed_line = f'{break_code}Type:{key}{break_code}'

                else:  # line press not equal to next line release
                    if self.debug:
                        print('\tNOT TAP')

                    # determine if the next line contains a wait command (must catch last line since there is not line after the last line)
                    next_line_wait = False
                    try:
                        if 'wait' in lines[index + 1].lower():
                            next_line_wait = True
                    except IndexError:
                        pass

                    if next_line_wait:  # if the next line is a wait command, process current line as is
                        processed_line = f'{break_code}{line}{break_code}'
                    else:
                        if 'Key' in line:
                            check_single_chars = {len(x) for x in pressed_keys if x != 'shift'} == {
                                1}  # all hotkeys are single chars
                            check_alphabet_letters = {((x.isalpha() and len(x) == 1) or (x=='space')) for x in pressed_keys if
                                                      (x != 'shift' and x not in symbol_chars)} == {
                                                         True}  # all hotkeys are single alphabetic characters
                            check_symbol_chars = {x for x in pressed_keys if
                                                  x in symbol_chars}  # any hotkeys are symbols

                            if 'press' in line:
                                if index != len(lines) - 1:
                                    if check_alphabet_letters and len(key) == 1 and key.isalpha():
                                        line = f'Type:{"".join(pressed_keys)}{key}'
                                        pressed_keys.clear()
                                    else:
                                        pressed_keys.append(key)
                                        pressed_keys = eliminate_duplicates(pressed_keys)
                                        line = ''

                            elif 'release' in line:
                                if key in pressed_keys:
                                    # execute hotkey
                                    if check_single_chars or len(pressed_keys) > 1:  # only process hotkey if there are multiple keys pressed
                                        if self.debug:
                                            print('\t\tregister hotkey: ', check_alphabet_letters)
                                        if 'shift' in pressed_keys and check_single_chars and (
                                                check_alphabet_letters or check_symbol_chars):
                                            line = f'Type:{"".join([x.capitalize() for x in pressed_keys if x != "shift"])}'
                                            pressed_keys.clear()
                                            # pressed_keys = []
                                        elif check_alphabet_letters:  # process release of key if pressed keys are alphabetic
                                            if key in pressed_keys:
                                                # pressed_keys.remove(key)
                                                if pressed_keys:
                                                    line = f'Type:{"".join(pressed_keys)}'
                                                pressed_keys.clear()
                                            else:
                                                line = ''
                                        else:
                                            line = f"Hotkey {' + '.join(pressed_keys)}"
                                            pressed_keys.clear()
                                    else:  # release with only one key pressed
                                        # do not process ctrl key release if previous line was not a ctrl key press
                                        if index > 0:
                                            if 'ctrl' in line and 'ctrl' not in lines[index-1]:
                                                line = ''
                                    if key in pressed_keys:
                                        pressed_keys.remove(key)

                                else:
                                    line = ''
                                    if check_alphabet_letters:  # process release of key if pressed keys are alphabetic
                                        if key in pressed_keys:
                                            # pressed_keys.remove(key)
                                            if pressed_keys:
                                                line = f'Type:{"".join(pressed_keys)}'

                                            pressed_keys.clear()

                            if self.debug:
                                print(f'\tpressed_keys: {pressed_keys}')

                        if line:
                            processed_line = f'{break_code}{line}{break_code}'
                        else:
                            processed_line = ''

                for master_key, replacement_keys in replacement_keys_ref.items():
                    for replacement_key in replacement_keys:
                        processed_line = processed_line.replace(replacement_key, master_key)

                processed_lines.append(processed_line)
                if self.debug:
                    print(f'\tprocessed_line: {[processed_line]}\n')
            else:
                skip = False

        if self.debug:
            print(f'processed_lines: {processed_lines}\n\n')
        processed_lines = ''.join(processed_lines).split(break_code)  # join lines and split on break_code
        processed_lines = [x for x in processed_lines if x]  # eliminate empty elements

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

        if self.debug:
            print(f'processed_lines: {processed_lines}\n\n')

        # consolidate consecutive type commands
        def consecutive_ranges_of(list_in):
            """Returns consecutive ranges of integers in list."""
            nums = sorted(set(list_in))
            gaps = [[start, end] for start, end in zip(nums, nums[1:]) if start + 1 < end]
            edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
            return list(zip(edges, edges))

        typing_indices = [index for index, line in enumerate(processed_lines) if 'Type:' in line]
        typing_ranges = consecutive_ranges_of(typing_indices)
        for typing_range in reversed(typing_ranges):
            if typing_range[0] != typing_range[1]:  # only if range is not a single index
                consolidated_type = ''
                for index in reversed(range(typing_range[0], typing_range[1] + 1)):
                    line = processed_lines[index]
                    consolidated_type = f"{re.compile(re.escape('type:'), re.IGNORECASE).sub('', line)}{consolidated_type}"
                    if index != typing_range[0]:
                        del processed_lines[index]
                processed_lines[typing_range[0]] = f'Type:{consolidated_type}'

        if self.debug:
            print(f'processed_lines: {processed_lines}\n\n')

        return processed_lines


class ExecutionThread(threading.Thread):
    """Worker Thread Class."""

    def __init__(self, parent):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self, daemon=True)
        self.parent = parent

    def run(self):
        """Run Worker Thread."""

        self.drag_duration_scale = math.hypot(pyauto.size().width, pyauto.size().width)
        self.lines_to_execute = self.parent.parent.lines.copy()
        self.type_interval = self.parent.execution_type_intrv
        self.mouse_duration = self.parent.execution_mouse_dur
        pyauto.PAUSE = self.parent.execution_pause

        self.mouse_down_coords = [0, 0]
        self.variables = dict()
        self.keep_running = True

        try:
            time.sleep(0.5)  # wait for last activating CTRL key to be released fully

            self.lines_should_be_executed = [True] * len(self.lines_to_execute)
            for line_index, line_orig in enumerate(self.lines_to_execute):
                if self.lines_should_be_executed[line_index]:
                    executed_start_index, executed_end_index = self.execute_line(line_orig, line_index)
                    self.lines_should_be_executed[executed_start_index:executed_end_index] = [False] * (
                            executed_end_index - executed_start_index)

        except pyauto.FailSafeException:
            self.keep_running = False

        try:
            if not self.keep_running:
                wx.PostEvent(self.parent,
                             ResultEvent('Failsafe triggered', self.parent.thread_event_id))
            else:
                wx.PostEvent(self.parent, ResultEvent('Completed!', self.parent.thread_event_id))
        except RuntimeError:
            print('Runtime error code kTPbmaAW66')
            raise SystemError('Runtime error code kTPbmaAW66')

    def execute_line(self, line_orig, line_index):
        if self.keep_running:  # only run when running
            line = line_orig.lower()
            line_first_word = line.strip().split(' ')[0]

            if 'type' in line_first_word[
                         :4]:  # 'type' command execution should be checked-for first because it may contain other command keywords
                line_orig = line_orig.replace('``nl``', '\n')  # replace custom new line delimiter
                line_orig = re.compile(re.escape('type:'), re.IGNORECASE).sub('', line_orig)  # replace 'Type:' command

                # replace variable names defined so far with values
                for var_to_type in variable_names_in(line_orig):
                    if var_to_type in self.variables:
                        line_orig = line_orig.replace(f'{{{{~{var_to_type}~}}}}', self.variables[var_to_type])

                # split up text to type into smaller groups to check for self.keep_running in between group execution
                num_char_per_execution = 2
                text_type_groups = [line_orig[ii:ii + num_char_per_execution] for ii in
                                    range(0, len(line_orig), num_char_per_execution)]

                pyauto.PAUSE = 0  # eliminate pauses between text_type_groups
                for text_type_group in text_type_groups:
                    if self.keep_running:
                        pyauto.typewrite(text_type_group, interval=self.type_interval)
                pyauto.PAUSE = self.parent.parent.execution_pause  # restore pauses after typing

            elif 'wait' in line_first_word[:4]:
                tot_time = float_in(line)
                time_floored = math.floor(
                    0.05 * math.floor(tot_time / 0.05))  # round down to nearest 0.05
                for half_sec_interval in range(
                        20 * time_floored):  # loop through each 0.05 second and if still running
                    if self.keep_running:
                        time.sleep(0.05)
                time.sleep(
                    tot_time - time_floored)  # wait additional time unaccounted for in rounding

            elif 'hotkey' in line_first_word[
                             :6]:  # 'hotkey' command execution should be checked-for before 'key' because 'key' is contained in 'hotkey'
                hotkeys = line.lower().replace('hotkey', '').replace(' ', '').split('+')
                pyauto.hotkey(
                    *hotkeys)  # the asterisk (*) unpacks the iterable list and passes each string as an argument

            elif 'key' in line_first_word[:3]:
                if 'tap' in line:
                    key = line.lower().replace('key', '').replace('tap', '').replace(' ', '')
                    pyauto.press(key)
                elif 'press' in line:
                    key = line.lower().replace('key', '').replace('press', '').replace(' ', '')
                    pyauto.keyDown(key)
                elif 'release' in line:
                    key = line.lower().replace('key', '').replace('release', '').replace(' ', '')
                    pyauto.keyUp(key)

            elif 'mouse-move' in line_first_word:
                coords = coords_of(line)
                pyauto.moveTo(x=coords[0], y=coords[1], duration=self.mouse_duration)

            elif 'double-click' in line_first_word:
                coords = coords_of(line)
                pyauto.click(clicks=2, x=coords[0], y=coords[1], duration=self.mouse_duration)

            elif 'triple-click' in line_first_word:
                coords = coords_of(line)
                pyauto.click(clicks=3, x=coords[0], y=coords[1], duration=self.mouse_duration)

            elif self.parent.parent.features_unlocked and ('assign' in line_first_word) and ('{{~' in line) and (
                    '~}}' in line):
                self.variables[variable_names_in(line_orig)[0]] = assignment_variable_value_in(
                    line_orig)  # store variable

            elif self.parent.parent.features_unlocked and ('if' in line_first_word) and ('{' in line):
                conditional_var = variable_names_in(line_orig)[0]

                conditional_operations = ['Equals', 'Not equal to', 'Contains', 'Is in', '>', '<', '≥',
                                          '≤']  # TODO import from compartmentalized softwareinfo module

                conditional_operation = conditional_operation_in(line_orig, conditional_operations)
                conditional_comparison = conditional_comparison_in(line_orig)

                conditional_satisfied = False
                try:
                    if conditional_operation == 'Equals':
                        if self.variables[conditional_var].strip() == conditional_comparison.strip():
                            conditional_satisfied = True
                    elif conditional_operation == 'Not equal to':
                        if self.variables[conditional_var] != conditional_comparison:
                            conditional_satisfied = True
                    elif conditional_operation == 'Contains':  # if var contains comparison
                        if conditional_comparison in self.variables[conditional_var]:
                            conditional_satisfied = True
                    elif conditional_operation == 'Is in':  # if var is in comparison
                        if self.variables[conditional_var] in conditional_comparison:
                            conditional_satisfied = True
                    elif conditional_operation == '>':
                        if float_in(self.variables[conditional_var]) > float_in(conditional_comparison):
                            conditional_satisfied = True
                    elif conditional_operation == '<':
                        if float_in(self.variables[conditional_var]) < float_in(conditional_comparison):
                            conditional_satisfied = True
                    elif conditional_operation == '≥':
                        if float_in(self.variables[conditional_var]) >= float_in(conditional_comparison):
                            conditional_satisfied = True
                    elif conditional_operation == '≤':
                        if float_in(self.variables[conditional_var]) <= float_in(conditional_comparison):
                            conditional_satisfied = True

                except KeyError:  # variable was not define prior to conditional evaluation
                    pass

                if not conditional_satisfied:
                    end_bracket_index = block_end_index(self.lines_to_execute, line_index)
                    self.lines_should_be_executed[line_index:end_bracket_index] = [False] * (
                            end_bracket_index - line_index)

            elif self.parent.parent.features_unlocked and ('loop' in line_first_word) and ('{' in line):
                loop_end_index = block_end_index(self.lines_to_execute, line_index)
                loop_lines = self.lines_to_execute[line_index + 1:loop_end_index]

                def execute_loop_block_lines(num_loop_iterations):
                    # reset lines_should_be_executed for lines in loop block to be executed below
                    self.lines_should_be_executed[line_index:loop_end_index] = [True] * (
                            loop_end_index - line_index)

                    loop_line_index = 0
                    for loop_line in loop_lines:
                        loop_line_index += 1
                        if self.lines_should_be_executed[line_index + loop_line_index]:
                            _, nested_loop_end_index = self.execute_line(loop_line,
                                                                         line_index + loop_line_index)

                            if loop_iteration == num_loop_iterations - 1:  # if last iteration has completed
                                # prevent future execution of lines that have already been executed by the loop logic
                                self.lines_should_be_executed[line_index:nested_loop_end_index] = [False] * (
                                        nested_loop_end_index - line_index)

                if 'multiple' in line:
                    num_times_to_loop = int(float_in(line))
                    for loop_iteration in range(num_times_to_loop):
                        execute_loop_block_lines(num_times_to_loop)

                if 'for each element in list' in line:
                    loop_list_text = line_orig[line_orig.find('[') + 1:line_orig.rfind(
                        ']')]  # find text between first '[' and last ']'
                    loop_list_values = loop_list_text.split("`'`")  # split based on delimiter

                    for loop_iteration, loop_list_value in enumerate(loop_list_values):
                        self.variables['loop.list.var'] = loop_list_value
                        execute_loop_block_lines(len(loop_list_values))

                return line_index, loop_end_index

            elif 'left-mouse' in line.strip().split(' ')[0] or 'right-mouse' in line.strip().split(' ')[0]:
                coords = coords_of(line)
                if 'right-mouse' in line:
                    btn = 'right'
                else:
                    btn = 'left'

                if 'click' in line:
                    pyauto.click(x=coords[0], y=coords[1], button=btn, duration=self.mouse_duration)
                elif 'press' in line:
                    pyauto.mouseDown(x=coords[0], y=coords[1], button=btn, duration=self.mouse_duration)
                    self.mouse_down_coords = coords
                elif 'release' in line:
                    drag_dist = math.hypot(self.mouse_down_coords[0] - coords[0],
                                           self.mouse_down_coords[1] - coords[1])
                    drag_duration = 0.5 * self.mouse_duration + (drag_dist / self.drag_duration_scale)
                    pyauto.moveTo(x=coords[0], y=coords[1], duration=drag_duration)
                    pyauto.mouseUp(button=btn)
                    time.sleep(0.5 * self.mouse_duration)

            return line_index, line_index + 1

    def abort(self):
        self.keep_running = False
        pyauto.FAILSAFE = False
        pyauto.PAUSE = 0.001
        for key in self.parent.parent.software_info.special_keys:  # release any problematic keys that may still be pressed
            pyauto.keyUp(key)
        pyauto.mouseUp(button='left')
        pyauto.PAUSE = self.parent.execution_pause
        pyauto.FAILSAFE = True


class ResultEvent(wx.PyEvent):
    """Event to carry result data."""

    def __init__(self, data, event_id):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(int(event_id))
        self.data = data


if __name__ == '__main__':  # debugging capability by running module file as main
    wx.DisableAsserts()  # disable alerts of non functioning wx.PostEvent

    # test listener_thread
    listener_thread = ListenerThread(None, wx.NewIdRef(), record=True, debug=True, record_pause=5)
    listener_thread.start()
    listener_thread.join()
