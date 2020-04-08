import math
import re
import threading
import time
import webbrowser

import pandas as pd
import pyautogui as pyauto
import wx
import wx.adv
import wx.lib.expando
import wx.lib.scrolledpanel
from pynput import keyboard, mouse


# TODO implement recording functionality
# TODO revise advanced edit guide styling
# TODO change attributes (self.var) to variables (var) where possible
# TODO comments
# TODO implement preference menu (autosave, default pauses, etc)
# TODO implement encrypted file storage for preferences and other data (resolution)
# TODO scrolled panel scroll down or up automatically
# TODO wx.adv.AnimationCtrl for wait animation
# TODO error codes with random generation for beta testing bug fixes
# TODO investigate image buttons (edit frame - back button)
# TODO image for recording, executing, and stopping (animation)
# TODO investigate compartmentalization for better organization
# TODO alternate row shading (edit frame)
# TODO investigate zoom
# TODO language switching
# TODO command move
# TODO control key validation
# TODO re-runs
# TODO create help guide
# TODO investigate compilation speed increases (numba, cpython, pypy)
# TODO investigate speed optimization by converting lists to sets used for 'in' comparisons
# TODO investigate speed optimization with multiprocessing
# TODO premium feature separation (any workflow destination)
# TODO for loops
# TODO variables from excel or in range, etc.
# TODO add Mac specific instructions (control --> command key) possibly ESC key?


def do_nothing(event=None):
    """Function to bind events to be disabled."""
    pass


def eliminate_duplicates(list_with_duplicates):
    """Function eliminate duplicates from list"""
    seen = set()
    seen_add = seen.add
    return [x for x in list_with_duplicates if not (x in seen or seen_add(x))]


def create_about_dialog(self):
    """Creates about dialog."""
    about_dlg = AboutDialog(self, 'About {}'.format(self.software_info.name))
    about_dlg.ShowModal()


def setup_frame(self, status_bar=False):
    """Setup standardized frame characteristics including file menu and status bar."""

    if status_bar:
        self.CreateStatusBar()

    # setting up the file menu
    file_menu = wx.Menu()
    menu_about = file_menu.Append(wx.ID_ABOUT, 'About', ' Information about {}'.format(self.software_info.name))
    self.Bind(wx.EVT_MENU, lambda event: on_about(self), menu_about)
    menu_exit = file_menu.Append(wx.ID_EXIT, 'Exit', 'Exit {}'.format(self.software_info.name))
    self.Bind(wx.EVT_MENU, lambda event: on_exit(self), menu_exit)

    # Menu for open option (future)
    # menu_open = file_menu.Append(wx.ID_OPEN, 'Open', ' Open a file to edit')
    # self.Bind(wx.EVT_MENU, self.OnOpen, menu_open)

    # create menu bar
    menu_bar = wx.MenuBar()
    menu_bar.Append(file_menu, 'File')  # Adding the file menu to the menu bar
    self.SetMenuBar(menu_bar)  # adding the menu bar to the Frame)

    self.SetIcon(wx.Icon('data/aldras.ico', wx.BITMAP_TYPE_ICO))  # assign icon

    self.SetBackgroundColour('white')  # set background color

    def on_about(self):
        create_about_dialog(self)

    def on_exit(self):
        self.Close()


def coords_of(line):
    """Returns tuple of parsed coordinates from string."""
    coords = line.split('(')[1].replace(' ', '').replace(')', '').split(',')
    try:
        x_coord = int(coords[0])
    except ValueError:  # usually occurs when string is empty
        x_coord = 0

    try:
        y_coord = int(coords[1])
    except ValueError:  # usually occurs when string is empty
        y_coord = 0

    coords = (x_coord, y_coord)
    return coords


def float_in(input_string):
    """Returns parsed float from string."""
    return float(re.findall(r'[-+]?\d*\.\d+|\d+', input_string)[0])


def consecutive_ranges_of(list_in):
    """Returns consecutive ranges of integers in list."""
    nums = sorted(set(list_in))
    gaps = [[start, end] for start, end in zip(nums, nums[1:]) if start + 1 < end]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))


def update_status_bar(parent, status):
    """Update status bar."""
    parent.StatusBar.SetStatusText(status)


def clear_status_bar(parent):
    """Clear status bar."""
    parent.StatusBar.SetStatusText('')


def config_status_and_tooltip(parent, obj_to_config, status, tooltip=True):
    """
    Configure status bar and tooltip for object.

    Parameters:
        parent (wx.Frame): The parent frame for which the status and tool tip should be configured.
        obj_to_config (wx.Widget): The widget for which the status and tool tip should be configured.
        status (str): The string that should be displayed for the status.
        tooltip (bool or str): 'True' should be passed if the tooltip should be configured with the status string. Another string should be passed if the tooltip should be configured with another string.
    """
    # TODO allow for just status bar or tooltip (for windows without status bars) -- TEST first (error with AdvancedEditGuide)
    obj_to_config.Bind(wx.EVT_ENTER_WINDOW, lambda event: update_status_bar(parent, '   ' + status))
    obj_to_config.Bind(wx.EVT_LEAVE_WINDOW, lambda event: clear_status_bar(parent))
    if isinstance(tooltip, str):
        obj_to_config.SetToolTip(tooltip)
    elif tooltip:
        obj_to_config.SetToolTip(status)


def output_to_file_bkup(output='', end='\n'):
    """Print string and write to file."""

    # TODO function still needed?
    try:
        global recording_lines
        recording_lines.append(output)
        print(recording_lines)
    except NameError:
        pass

    output = (output + end)

    # Will add back when recording is enabled
    # with open('{}_bkup.txt'.format(workflow_name), 'a') as record_file:
    #     record_file.write(''.join(output))
    # print(output, end='')


def on_press_recording(key):
    """Process keystroke press for keyboard listener for ListenerThread instances."""
    global capslock
    global ctrls
    global in_action
    output = str(key).strip('\'').lower()
    coords = ''
    if in_action:
        if output == 'key.caps_lock':  # if capslock pressed, swap capslock state
            capslock = not capslock
        if output == 'key.ctrl_l':  # if left ctrl is pressed, record current mouse position
            coords = pyauto.position()
        if not output.startswith('key'):  # i.e., if output is alphanumeric
            if capslock:
                output = output.swapcase()
        if (output.startswith('\\') and output != '\\\\') or (
                output.startswith('<') and output.endswith('>')):  # substituted ctrl+_key_ value
            output = '{}'.format(ctrl_keys_df['Translation'][output.replace('<', '').replace('>', '')])
        if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
            output_to_file_bkup('Key \\ press')
            output = ''
        if output == '\"\'\"':
            output = '\''
        if (not output.startswith('key.ctrl_r')) and (
                not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
            if 'key.' in output:
                output = output.replace('key.', '')
            output = 'Key ' + output + ' press'
            if coords:
                output = output + ' at {}'.format((coords[0], coords[1]))
            output_to_file_bkup(output)
    if 'key.ctrl_r' in output:
        ctrls += 1
        print('{}  '.format(ctrls), end='')
        if not in_action:
            if ctrls == 1:
                event_message = 'Action in 3'
            elif ctrls == 2:
                event_message = 'Action in 3 2'
            elif ctrls == 3:
                event_message = 'Action'
        elif in_action:
            if ctrls == 1:
                event_message = 'Stopping in 3'
            elif ctrls == 2:
                event_message = 'Stopping in 3 2'
            elif ctrls == 3:
                event_message = 'Completed!'
        else:
            event_message = 'Error!'

        wx.PostEvent(listener_thread.parent, ResultEvent('{}'.format(event_message)))

        # TODO revisit and optimize
        if ctrls >= 3:
            ctrls = 0
            in_action = not in_action
            print()
            print('RECORDING = {}'.format(in_action))
            if not in_action:
                print('Complete!')
                # compile_recording()
                raise SystemExit()


def on_release_recording(key):
    """Process keystroke release for keyboard listener for ListenerThread instances."""
    # TODO revisit and optimize
    global capslock
    global ctrls
    global in_action
    output = str(key).strip('\'').lower()
    coords = ''
    if in_action:
        if output == 'key.ctrl_l':  # if left ctrl is pressed, record current mouse position
            coords = pyauto.position()
        if not output.startswith('key'):  # i.e., if output is alphanumeric
            if capslock:
                output = output.swapcase()
        if (output.startswith('\\') and output != '\\\\') or (
                output.startswith('<') and output.endswith('>')):  # substituted ctrl+_key_ value
            output = '{}'.format(ctrl_keys_df['Translation'][output.replace('<', '').replace('>', '')])
        if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
            output_to_file_bkup('Key \\ release')
            output = ''
        if output == '\"\'\"':
            output = '\''
        if (not output.startswith('key.ctrl_r')) and (
                not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
            if 'key.' in output:
                output = output.replace('key.', '')
            output = 'Key ' + output + ' release'
            if coords:
                output = output + ' at {}'.format((coords[0], coords[1]))
            output_to_file_bkup(output)


def on_click_recording(x, y, button, pressed):
    """Process click for mouse listener for ListenerThread instances."""
    if in_action:
        output_to_file_bkup('{}-mouse {} at {}'.format(str(button).replace('Button.', '').capitalize(),
                                                       'press' if pressed else 'release', (x, y)))


def thread_event_handler(win, func):
    """Process message events from threads."""
    win.Connect(-1, -1, int(EVT_RESULT_ID), func)


class AboutDialog(wx.Dialog):
    def __init__(self, parent, caption):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)  # | wx.RESIZE_BORDER)
        self.SetTitle(caption)
        self.SetBackgroundColour('white')
        self.SetIcon(wx.Icon('data/aldras.ico', wx.BITMAP_TYPE_ICO))
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.FlexGridSizer(2, 1, 10, 10)

        self.vbox_top = wx.BoxSizer(wx.VERTICAL)

        self.hbox_logo_name_version = wx.BoxSizer(wx.HORIZONTAL)

        # add rescaled logo image
        png = wx.Image('data/aldras.png', wx.BITMAP_TYPE_PNG).Scale(150, 150, quality=wx.IMAGE_QUALITY_HIGH)
        self.logo_img = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(png))
        self.hbox_logo_name_version.Add(self.logo_img, 0, wx.ALIGN_CENTER_VERTICAL)
        self.vbox_name_version = wx.BoxSizer(wx.VERTICAL)

        # add program name text
        self.program_name = wx.StaticText(self, label='{} Automation'.format(parent.software_info.name))
        self.program_name.SetFont(wx.Font(wx.FontInfo(18)))  # change font
        self.program_name.SetForegroundColour(3 * (20,))  # change font color to (r,g,b)
        self.vbox_name_version.Add(self.program_name, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program version text
        self.program_version = wx.StaticText(self, label='Version {}'.format(parent.software_info.version))
        self.program_version.SetFont(wx.Font(wx.FontInfo(10)).Italic())  # change font
        self.program_version.SetForegroundColour(3 * (80,))  # change font color to (r,g,b)
        self.vbox_name_version.Add(self.program_version, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.hbox_logo_name_version.Add(self.vbox_name_version, 0, wx.ALIGN_CENTER_VERTICAL)
        self.vbox_top.Add(self.hbox_logo_name_version, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program description text
        self.program_description = wx.StaticText(self, label=parent.software_info.description)
        self.program_description.SetFont(wx.Font(wx.FontInfo(10)))  # change font
        self.program_description.SetForegroundColour(3 * (40,))  # change font color to (r,g,b)
        self.vbox_top.Add(self.program_description, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program link
        self.program_link = wx.adv.HyperlinkCtrl(self, label=parent.software_info.website,
                                                 url=parent.software_info.website)
        self.vbox_top.Add(self.program_link, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH, 15)

        # add copyright
        self.program_copyright = wx.StaticText(self, label='© {}'.format(parent.software_info.copyright))
        self.vbox_top.Add(self.program_copyright, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH, 10)

        self.hbox_btns = wx.BoxSizer(wx.HORIZONTAL)

        # add license button
        self.license_btn = wx.Button(self, label='License')
        self.license_btn.SetFocus()
        self.license_btn.Bind(wx.EVT_BUTTON, self.licence)
        self.hbox_btns.Add(self.license_btn)

        self.hbox_btns.AddStretchSpacer()
        self.hbox_btns.AddSpacer(5)
        self.hbox_btns.AddStretchSpacer()

        # add privacy statement button
        self.privacy_btn = wx.Button(self, label='Privacy Statement')
        self.privacy_btn.Bind(wx.EVT_BUTTON, self.privacy)
        self.hbox_btns.Add(self.privacy_btn)

        self.vbox.AddMany([(self.vbox_top, 0, wx.EXPAND | wx.NORTH | wx.EAST | wx.WEST, 40),
                           (self.hbox_btns, 0, wx.EXPAND | wx.NORTH, 20)])

        self.vbox_outer.Add(self.vbox, 0, wx.ALL, 5)
        self.SetSizerAndFit(self.vbox_outer)

    def licence(self, event):
        webbrowser.open_new_tab('https://aldras.com/')

    def privacy(self, event):
        webbrowser.open_new_tab('https://aldras.com/')


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(int(EVT_RESULT_ID))
        self.data = data


class ListenerThread(threading.Thread):
    """Worker Thread Class."""

    def __init__(self, parent, listen_to_key=True, listen_to_mouse=True, record=False):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self, daemon=True)
        global listener_thread
        listener_thread = self
        self.parent = parent
        self.listen_to_key = listen_to_key
        self.listen_to_mouse = listen_to_mouse
        self.record = record
        if self.record:
            global recording_lines
            recording_lines = []
        try:
            global ctrl_keys_df
            ctrl_keys_df = pd.read_csv('ctrl_keys_ref.csv',
                                       names=['Translation',
                                              'Code'])  # reference for all ctrl hotkeys (registered as separate key)
            ctrl_keys_df = ctrl_keys_df.set_index('Code')
        except FileNotFoundError as e:
            print('FileNotFoundError: [Errno 2] File ctrl_keys_ref.csv does not exist: \'ctrl_keys_ref.csv\'')
            time.sleep(3)
            raise FileNotFoundError

    def run(self):
        """Run worker thread."""
        global in_action
        global ctrls
        in_action = False
        ctrls = 0

        if self.listen_to_key:
            self.key_listener = keyboard.Listener(on_press=on_press_recording, on_release=on_release_recording)
            self.key_listener.start()
        if self.listen_to_mouse:
            self.mouse_listener = mouse.Listener(
                on_click=on_click_recording)  # , on_scroll=on_scroll_recording, on_move=on_move_recording)
            self.mouse_listener.start()

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
        global recording_lines
        lines = recording_lines
        print('lines: {}'.format(lines))

        mouse_hover_duration = 0.5
        processed_lines = []
        skip = False
        break_code = '```8729164788```'
        break_value = ''
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
                print('line: {}'.format(line))
                key = line.split(' ')[1]
                print('key: {}'.format(key))

                if not pressed_keys and lines[index].replace('press', '') == lines[index + 1].replace('release',
                                                                                                      ''):  # if line press is same as next line release
                    print('ONLY TAP')

                    skip = True  # skip the next (release) line
                    if len(key) > 1:  # special functions

                        if 'ctrl_l' in line:  # if left ctrl is in line signalling mouse-move
                            coords = coords_of(line)
                            line = 'Mouse-move to {}{}Wait {}{}'.format((coords[0], coords[1]), break_code,
                                                                        mouse_hover_duration, break_code)

                        elif key == 'space':
                            line = 'Type: '

                        else:
                            if 'mouse' in line:
                                tap_replacement = 'click'
                            else:
                                tap_replacement = 'tap'
                            line = lines[index].replace('press', tap_replacement)

                        processed_line = break_code + line + break_code

                    else:  # alphanumeric keys (try to compile into type command)
                        processed_line = break_code + 'Type:{}'.format(key) + break_code

                else:  # line press not equal to next line release
                    print('NOT TAP: {}'.format(line))
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
                                    line = 'Type:{}'.format(
                                        ''.join([x.capitalize() for x in pressed_keys if x != 'shift']))
                                    # pressed_keys = []
                                else:
                                    line = 'Hotkey {}'.format(' + '.join(pressed_keys))
                            else:
                                line = ''
                            register_hotkey = False
                            if key in pressed_keys:
                                pressed_keys.remove(key)

                        print('pressed_keys: {}'.format(pressed_keys))

                    # else:
                    if line:
                        processed_line = break_code + line + break_code
                    else:
                        processed_line = ''

                for master_key, replacement_keys in replacement_keys_ref.items():
                    for replacement_key in replacement_keys:
                        processed_line = processed_line.replace(replacement_key, master_key)

                processed_lines.append(processed_line)
                print('processed_line: {}'.format(processed_line))
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
                    processed_lines[index] = 'Triple-click at {}\n'.format(coords_of(tripleA))
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
                    processed_lines[index] = 'Double-click at {}\n'.format(coords_of(pairA))
                    processed_lines_to_remove.append(index + 1)
                    processed_lines[index + 1] = ''
        for index in processed_lines_to_remove[::-1]:
            processed_lines.pop(index)

        print(processed_lines)

        # consolidate consecutive type commands
        typing_indices = [index for index, line in enumerate(processed_lines) if 'Type:' in line]
        typing_ranges = consecutive_ranges_of(typing_indices)
        print(list(reversed(typing_ranges)))
        for typing_range in reversed(typing_ranges):
            if typing_range[0] != typing_range[1]:  # only if range is not a single index
                consolidated_type = ''
                for index in reversed(range(typing_range[0], typing_range[1] + 1)):
                    line = processed_lines[index]
                    consolidated_type = line.replace('Type:', '') + consolidated_type
                    if index != typing_range[0]:
                        del processed_lines[index]
                processed_lines[typing_range[0]] = 'Type:{}'.format(consolidated_type)

        print(processed_lines)
        return processed_lines


class RecordingThread(threading.Thread):
    """Worker Thread Class."""

    def __init__(self, parent):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self, daemon=True)
        self.parent = parent

    def run(self):
        """Run Worker Thread."""

        drag_duration_scale = math.hypot(pyauto.size().width, pyauto.size().width)
        lines = self.parent.parent.lines
        pause = self.parent.parent.execution_pause
        type_interval = self.parent.parent.execution_type_intrv
        mouse_duration = self.parent.parent.execution_mouse_dur

        mouse_down_coords = [0, 0]
        pyauto.PAUSE = pause
        self.keep_running = True

        try:
            for line_orig in lines:
                if self.keep_running:
                    line = line_orig.replace('\n', '').lower()
                    print(line)

                    if 'type' in line:  # 'type' command execution should be checked-for first because it may contain other command keywords
                        pyauto.typewrite(
                            line_orig.replace('\n', '').replace('Type:', '').replace('type:', ''),
                            interval=type_interval)

                    elif 'wait' in line:
                        time.sleep(float_in(line))

                    elif 'left-mouse' in line or 'right-mouse' in line:
                        coords = coords_of(line)
                        if 'right-mouse' in line:
                            btn = 'right'
                        else:
                            btn = 'left'

                        if 'click' in line:
                            pyauto.click(x=coords[0], y=coords[1], button=btn)
                        elif 'press' in line:
                            pyauto.mouseDown(x=coords[0], y=coords[1], button=btn)
                            mouse_down_coords = coords
                        elif 'release' in line:
                            drag_dist = math.hypot(mouse_down_coords[0] - coords[0], mouse_down_coords[1] - coords[1])
                            drag_duration = 0.5 * mouse_duration + (drag_dist / drag_duration_scale)
                            pyauto.moveTo(x=coords[0], y=coords[1], duration=drag_duration)
                            pyauto.mouseUp(button=btn)
                            time.sleep(0.5 * mouse_duration)

                    elif 'hotkey' in line:  # 'hotkey' command execution should be checked-for before 'key' because 'key' is
                        # contained in 'hotkey'
                        hotkeys = line.replace('hotkey ', '').split('+')
                        pyauto.hotkey(
                            *hotkeys)  # the asterisk (*) unpacks the iterable list and passes each string as an argument

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

            wx.PostEvent(self.parent, ResultEvent('{}'.format('Completed!')))
        except pyauto.FailSafeException:
            wx.PostEvent(self.parent, ResultEvent('{}'.format('Failsafe triggered')))

    def abort(self):
        self.keep_running = False


class ExecutionThread(threading.Thread):
    """Worker Thread Class."""

    def __init__(self, parent):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self, daemon=True)
        self.parent = parent
        # global execution_thread
        # execution_thread = self
