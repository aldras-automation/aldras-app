import math
import os
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

# TODO implement changing edit commands updating
# TODO change 'tap' to 'click'
# TODO change 'sleep' to 'wait'
# TODO revise advanced edit guide styling
# TODO comments
# TODO implement preference menu (autosave, default pauses, etc)
# TODO implement encrypted file storage for preferences and other data (resolution)
# TODO scrolled panel scroll down or up automatically
# TODO wx.adv.AnimationCtrl for wait animation
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

EVT_RESULT_ID = wx.NewIdRef()  # global variable needed for threading event receiving


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

    self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))  # assign icon

    self.SetBackgroundColour('white')  # set background color

    def on_about(self):
        create_about_dialog(self)

    def on_exit(self):
        self.Close()


def coords_of(line):
    """Returns tuple of parsed coordinates from string."""
    coords = line.split('(')[1].replace(' ', '').replace(')', '').split(',')
    coords = (int(coords[0]), int(coords[1]))
    return coords


def float_in(input_string):
    """Returns parsed float from string."""
    return float(re.findall(r'[-+]?\d*\.\d+|\d+', input_string)[0])


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
    # TODO allow for just status bar or tooltip (for windows without status bars) -- TEST first
    obj_to_config.Bind(wx.EVT_ENTER_WINDOW, lambda event: update_status_bar(parent, '   ' + status))
    obj_to_config.Bind(wx.EVT_LEAVE_WINDOW, lambda event: clear_status_bar(parent))
    if isinstance(tooltip, str):
        obj_to_config.SetToolTip(tooltip)
    elif tooltip:
        obj_to_config.SetToolTip(status)


def output_to_file_bkup(output='', end='\n'):
    """Print string and write to file."""

    # TODO function still needed?

    output = (output + end)
    # Will add back when recording is enabled
    # with open('{}_bkup.txt'.format(workflow_name), 'a') as record_file:
    #     record_file.write(''.join(output))
    print(output, end='')
    return


def on_press_recording(key):
    """Process keystroke press for keyboard listener for ListenerThread instances."""
    global capslock
    global ctrls
    global in_action
    output = str(key).strip('\'').lower()
    coords = ''
    df = pd.read_csv('ctrl_keys_ref.csv',
                     names=['Translation', 'Code'])  # reference for all ctrl hotkeys (registered as separate key)
    df = df.set_index('Code')
    if in_action:
        if output == 'key.caps_lock':  # if capslock pressed, swap capslock state
            capslock = not capslock
        if output == 'key.space':
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
    return


def on_release_recording(key):
    """Process keystroke release for keyboard listener for ListenerThread instances."""
    # TODO revisit and optimize
    global capslock
    global ctrls
    global in_action
    output = str(key).strip('\'').lower()
    coords = ''
    if in_action:
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
    """Process click for mouse listener for ListenerThread instances."""
    if in_action:
        output_to_file_bkup('``{}```{} at {}'.format(str(button).lower(), 'pressed' if pressed else 'released', (x, y)))
    return


def on_scroll_recording(x, y, dx, dy):
    """Process scroll for mouse listener for ListenerThread instances."""
    if in_action:
        output_to_file_bkup('``scrolled.{}```1 at {}'.format('down' if dy < 0 else 'up', (x, y)))
    return


def on_move_recording(x, y):
    """Process move for mouse listener for ListenerThread instances."""
    # if recording:
    #     output_to_file_bkup('``moved```{}'.format((x, y)))
    return


def thread_event_handler(win, func):
    """Process message events from threads."""
    win.Connect(-1, -1, int(EVT_RESULT_ID), func)


class AboutDialog(wx.Dialog):
    def __init__(self, parent, caption):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)  # | wx.RESIZE_BORDER)
        self.SetTitle(caption)
        self.SetBackgroundColour('white')
        self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.FlexGridSizer(2, 1, 10, 10)

        self.vbox_top = wx.BoxSizer(wx.VERTICAL)

        self.hbox_logo_name_version = wx.BoxSizer(wx.HORIZONTAL)

        # add rescaled logo image
        png = wx.Image('logo.png', wx.BITMAP_TYPE_PNG).Scale(150, 150, quality=wx.IMAGE_QUALITY_HIGH)
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

    def __init__(self, parent, listen_to_key=True, listen_to_mouse=True):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self, daemon=True)
        global listener_thread
        listener_thread = self
        self.parent = parent
        self.listen_to_key = listen_to_key
        self.listen_to_mouse = listen_to_mouse

    def run(self):
        """Run Worker Thread."""
        global in_action
        global ctrls
        in_action = False
        ctrls = 0

        if self.listen_to_key:
            self.key_listener = keyboard.Listener(on_press=on_press_recording, on_release=on_release_recording)
            self.key_listener.start()
        if self.listen_to_mouse:
            self.mouse_listener = mouse.Listener(on_click=on_click_recording, on_scroll=on_scroll_recording,
                                                 on_move=on_move_recording)
            self.mouse_listener.start()
        # self.listener.join()

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        if self.listen_to_key:
            self.key_listener.stop()
        if self.listen_to_mouse:
            self.mouse_listener.stop()


class ExecutionThread(threading.Thread):
    """Worker Thread Class."""

    def __init__(self, parent):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self, daemon=True)
        self.parent = parent
        global execution_thread
        execution_thread = self

    def run(self):
        """Run Worker Thread."""
        # execute(self.parent.parent.lines, pause=0.2)

        drag_duration_scale = math.hypot(pyauto.size().width, pyauto.size().width)
        lines = self.parent.parent.lines
        pause = self.parent.parent.execution_pause
        type_interval = self.parent.parent.execution_type_intrv
        mouse_duration = self.parent.parent.execution_mouse_dur

        # print('pause - run: {}'.format(type(self.parent.parent.execution_pause)))
        # print('execution_mouse_dur - run: {}'.format(type(self.parent.parent.execution_mouse_dur)))
        # print('execution_type_intrv - run: {}'.format(type(self.parent.parent.execution_type_intrv)))

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
                            line_orig.replace('\n', '').replace('Type: ', '').replace('type: ', '').replace('Type:',
                                                                                                            '').replace(
                                'type:', ''), interval=type_interval)

                    elif 'sleep' in line:
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


class RecordCtrlCounterDialog(wx.Dialog):
    def __init__(self, parent, caption):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)
        self.SetTitle(caption)
        self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour('white')
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.directions_a_rest = ': Press the right control key 3 times'

        self.directions_a = wx.StaticText(self, label='Start' + self.directions_a_rest)
        self.directions_a.SetFont(wx.Font(wx.FontInfo(14)))  # change font size
        self.vbox.Add(self.directions_a, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.vbox.AddSpacer(30)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.countdown_dark = wx.StaticText(self, label=''.format(parent.workflow_name))
        self.countdown_dark.SetFont(wx.Font(wx.FontInfo(22)))  # change font size
        self.hbox.Add(self.countdown_dark)
        self.countdown_dark.Show(False)

        self.countdown_light = wx.StaticText(self, label=''.format(parent.workflow_name))
        self.countdown_light.SetFont(wx.Font(wx.FontInfo(22)))  # change font size
        self.countdown_light.SetForegroundColour(3 * (150,))  # change font color to (r,g,b)
        self.hbox.Add(self.countdown_light)
        self.countdown_light.Show(False)

        self.vbox.Add(self.hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.vbox.AddSpacer(20)

        self.recording_message_a = wx.StaticText(self, label='Now recording clicks and keypresses')
        self.recording_message_a.SetFont(wx.Font(wx.FontInfo(13)))  # change font size
        self.recording_message_a.SetForegroundColour((170, 20, 20))  # change font color to (r,g,b)
        self.vbox.Add(self.recording_message_a, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.recording_message_a.Show(False)

        self.vbox.AddSpacer(5)

        self.recording_message_b = wx.StaticText(self, label='Left control key: record mouse position')
        self.recording_message_b.SetFont(wx.Font(wx.FontInfo(10)))  # change font size
        self.recording_message_b.SetForegroundColour((170, 20, 20))  # change font color to (r,g,b)
        self.vbox.Add(self.recording_message_b, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.recording_message_b.Show(False)

        self.spacer_a = wx.StaticText(self, label='')
        self.spacer_a.SetFont(wx.Font(wx.FontInfo(5)))  # change font size
        self.vbox.Add(self.spacer_a, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.spacer_a.Show(False)

        self.finish_btn = wx.Button(self, label='Finish')
        self.finish_btn.Bind(wx.EVT_BUTTON, self.close_window)
        self.vbox.Add(self.finish_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EAST | wx.WEST, 100)
        self.finish_btn.Show(False)

        self.spacer_b = wx.StaticText(self, label='')
        self.spacer_b.SetFont(wx.Font(wx.FontInfo(20)))  # change font size
        self.vbox.Add(self.spacer_b, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.spacer_b.Show(False)

        self.vbox_outer.Add(self.vbox, 0, wx.NORTH | wx.WEST | wx.EAST, 50)
        self.SetSizerAndFit(self.vbox_outer)

        # Set up event handler for any worker thread results
        thread_event_handler(self, self.read_thread_event_input)

        self.start_listener()

        self.Bind(wx.EVT_CLOSE, self.close_window)

    def start_listener(self):
        """Start Computation."""
        self.listener_thread = ListenerThread(self)
        self.listener_thread.start()

    def read_thread_event_input(self, event):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            self.countdown_light.SetLabel('Some error occurred')
            self.countdown_light.Show(True)
        else:  # Process results
            self.countdown_dark.Show(True)
            self.countdown_light.Show(True)

            self.countdown_dark.SetLabel(event.data.replace('Action', 'Recording'))
            self.countdown_dark.SetForegroundColour(wx.BLACK)

            if event.data == 'Action in 3':
                self.countdown_light.SetLabel(' 2 1')
                self.spacer_b.Show(True)

            elif event.data == 'Action in 3 2':
                self.countdown_light.SetLabel(' 1')

            elif event.data == 'Action':
                self.countdown_dark.SetForegroundColour((170, 20, 20))  # change font color to (r,g,b)
                self.directions_a.SetLabel('Stop' + self.directions_a_rest)
                self.countdown_light.SetLabel('')
                self.countdown_light.Show(False)
                self.recording_message_a.Show(True)
                self.recording_message_b.Show(True)

            elif event.data == 'Stopping in 3':
                self.countdown_light.SetLabel(' 2 1')

            elif event.data == 'Stopping in 3 2':
                self.countdown_light.SetLabel(' 1')

            elif event.data == 'Completed!':
                self.directions_a.Show(False)
                self.countdown_light.SetLabel('')
                self.countdown_light.Show(False)
                self.countdown_dark.SetFont(wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.NORMAL))  # change font size
                self.recording_message_a.Show(False)
                self.recording_message_b.Show(False)
                self.spacer_a.Show(True)
                self.finish_btn.Show(True)

            self.vbox.Layout()
            self.vbox_outer.Layout()
            self.SetSizerAndFit(self.vbox_outer)
            self.Fit()

    def close_window(self, event):
        self.listener_thread.abort()
        print(self.listener_thread)
        self.Destroy()


class ExecuteCtrlCounterDialog(wx.Dialog):
    def __init__(self, parent, caption):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.SetTitle(caption)
        self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour('white')
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.directions_a = wx.StaticText(self, label='Start: Press the right control key 3 times')
        self.directions_a.SetFont(wx.Font(wx.FontInfo(14)))  # change font size
        self.vbox.Add(self.directions_a, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.vbox.AddSpacer(10)

        self.directions_b = wx.StaticText(self, label='Stop: Move the mouse to the upper-left screen corner')
        self.directions_b.SetFont(wx.Font(wx.FontInfo(14)))  # change font size
        self.directions_b.SetForegroundColour((170, 20, 20))  # change font color to (r,g,b)
        self.vbox.Add(self.directions_b, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.vbox.AddSpacer(30)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.countdown_dark = wx.StaticText(self, label=''.format(parent.workflow_name))
        self.countdown_dark.SetFont(wx.Font(wx.FontInfo(22)))  # change font size
        self.hbox.Add(self.countdown_dark)
        self.countdown_dark.Show(False)

        self.countdown_light = wx.StaticText(self, label=''.format(parent.workflow_name))
        self.countdown_light.SetFont(wx.Font(wx.FontInfo(22)))  # change font size
        self.countdown_light.SetForegroundColour(3 * (150,))  # change font color to (r,g,b)
        self.hbox.Add(self.countdown_light)
        self.countdown_light.Show(False)

        self.vbox.Add(self.hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.vbox.AddSpacer(20)

        self.executing_message_a = wx.StaticText(self, label='Now executing clicks and keypresses')
        self.executing_message_a.SetFont(wx.Font(wx.FontInfo(13)))  # change font size
        self.executing_message_a.SetForegroundColour((20, 120, 20))  # change font color to (r,g,b)
        self.vbox.Add(self.executing_message_a, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.executing_message_a.Show(False)

        self.spacer_a = wx.StaticText(self, label='')
        self.spacer_a.SetFont(wx.Font(wx.FontInfo(5)))  # change font size
        self.vbox.Add(self.spacer_a, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.spacer_a.Show(False)

        self.finish_btn = wx.Button(self, label='Finish')
        self.finish_btn.Bind(wx.EVT_BUTTON, self.close_window)
        self.vbox.Add(self.finish_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EAST | wx.WEST, 100)
        self.finish_btn.Show(False)

        self.spacer_b = wx.StaticText(self, label='')
        self.spacer_b.SetFont(wx.Font(wx.FontInfo(20)))  # change font size
        self.vbox.Add(self.spacer_b, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.spacer_b.Show(False)

        self.vbox_outer.Add(self.vbox, 0, wx.NORTH | wx.WEST | wx.EAST, 50)
        self.SetSizerAndFit(self.vbox_outer)

        # Set up event handler for any worker thread results
        thread_event_handler(self, self.read_thread_input)

        self.start_listener()

        self.Bind(wx.EVT_CLOSE, self.close_window)

    def start_listener(self):
        """Start Computation."""
        self.listener_thread = ListenerThread(self, listen_to_key=True, listen_to_mouse=False)
        self.listener_thread.start()

    def start_execution_thread(self):
        self.execution_thread = ExecutionThread(self)
        self.execution_thread.start()

    def read_thread_input(self, event):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            self.countdown_light.SetLabel('Some error occurred')
            self.countdown_light.Show(True)
        else:  # Process results
            self.countdown_dark.Show(True)
            self.countdown_light.Show(True)

            self.countdown_dark.SetLabel(event.data.replace('Action', 'Executing'))
            self.countdown_dark.SetForegroundColour(wx.BLACK)

            if event.data == 'Action in 3':
                self.countdown_light.SetLabel(' 2 1')
                self.spacer_b.Show(True)

            elif event.data == 'Action in 3 2':
                self.countdown_light.SetLabel(' 1')

            elif event.data == 'Action':
                self.countdown_dark.SetForegroundColour((20, 120, 20))  # change font color to (r,g,b)
                self.countdown_light.SetLabel('')
                self.countdown_light.Show(False)
                self.executing_message_a.Show(True)
                self.start_execution_thread()

            elif event.data == 'Stopping in 3':
                self.countdown_light.SetLabel(' 2 1')

            elif event.data == 'Stopping in 3 2':
                self.countdown_light.SetLabel(' 1')

            elif event.data == 'Completed!':
                self.directions_a.Show(False)
                self.directions_b.Show(False)
                self.countdown_light.SetLabel('')
                self.countdown_light.Show(False)
                self.countdown_dark.SetFont(wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.NORMAL))  # change font size
                self.executing_message_a.Show(False)
                self.spacer_a.Show(True)
                self.finish_btn.Show(True)

            elif event.data == 'Failsafe triggered':
                print('Failsafe triggered')
                self.listener_thread.abort()
                self.execution_thread.abort()

                self.directions_a.Show(False)
                self.directions_b.SetLabel('Top-Left Corner Failsafe Triggered')
                self.countdown_light.SetLabel('')
                self.countdown_light.Show(False)
                self.countdown_dark.SetLabel('Execution Stopped')
                self.countdown_dark.SetFont(wx.Font(22, wx.DEFAULT, wx.ITALIC, wx.NORMAL))  # change font size
                self.countdown_dark.SetForegroundColour((170, 20, 20))  # change font color to (r,g,b)
                self.executing_message_a.Show(False)
                self.spacer_a.Show(True)
                self.finish_btn.Show(True)

            self.vbox.Layout()
            self.vbox_outer.Layout()
            self.SetSizerAndFit(self.vbox_outer)
            self.Fit()

    def close_window(self, event):
        self.listener_thread.abort()
        self.execution_thread.abort()
        print(self.listener_thread)
        print(self.execution_thread)
        self.Destroy()


class RecordDialog(wx.Dialog):
    def __init__(self, parent, caption):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)
        self.SetTitle(caption)
        self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour('white')
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox_options = wx.BoxSizer(wx.HORIZONTAL)

        self.some_sleep_thresh = 0.2

        self.sleep_box = wx.StaticBox(self, wx.ID_ANY, 'Record pause')
        self.sleep_sizer = wx.StaticBoxSizer(self.sleep_box, wx.VERTICAL)

        self.record_no_sleep = wx.RadioButton(self, wx.ID_ANY, 'No pauses')
        self.record_no_sleep.SetValue(True)
        self.record_no_sleep.Bind(wx.EVT_RADIOBUTTON, lambda event: self.not_some_sleep_pressed())
        self.sleep_sizer.Add(self.record_no_sleep, 0, wx.ALL, 4)

        self.record_all_sleep = wx.RadioButton(self, wx.ID_ANY, 'All pauses')
        self.record_all_sleep.Bind(wx.EVT_RADIOBUTTON, lambda event: self.not_some_sleep_pressed())
        self.sleep_sizer.Add(self.record_all_sleep, 0, wx.ALL, 4)

        self.some_sleep_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.some_sleep_hbox.AddSpacer(4)
        self.record_some_sleep = wx.RadioButton(self, wx.ID_ANY, 'Pauses over')
        self.record_some_sleep.Bind(wx.EVT_RADIOBUTTON, lambda event: self.record_some_sleep_pressed())
        self.some_sleep_hbox.Add(self.record_some_sleep, 0, wx.ALIGN_CENTER_VERTICAL)

        self.some_sleep_thresh = PlaceholderTextCtrl(self, wx.ID_ANY, placeholder='0.2', size=wx.Size(50, -1),
                                                     style=wx.TE_CENTER)
        self.some_sleep_thresh.Enable(False)
        self.some_sleep_hbox.Add(self.some_sleep_thresh)

        self.some_sleep_hbox.Add(wx.StaticText(self, label='  sec   '), 0, wx.ALIGN_CENTER_VERTICAL)
        self.sleep_sizer.Add(self.some_sleep_hbox, 0, wx.BOTTOM, 5)

        self.hbox_options.Add(self.sleep_sizer, 0, wx.ALL, 5)

        self.hbox_options.AddSpacer(5)

        self.record_mthd = wx.RadioBox(self, label='Method', choices=['Overwrite', 'Append'], majorDimension=1,
                                       style=wx.RA_SPECIFY_COLS)
        self.record_mthd.SetItemToolTip(0, 'Erase existing data')
        self.record_mthd.SetItemToolTip(1, 'Add to end of existing data')
        self.hbox_options.Add(self.record_mthd, 0, wx.ALL, 5)

        self.vbox.Add(self.hbox_options, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.vbox.AddSpacer(10)

        self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)

        self.vbox.Add(self.btns, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.vbox_outer.Add(self.vbox, 0, wx.ALL, 10)
        self.SetSizerAndFit(self.vbox_outer)

    def record_some_sleep_pressed(self):
        self.some_sleep_thresh.Enable(True)

    def not_some_sleep_pressed(self):
        self.some_sleep_thresh.Enable(False)


class ExecuteDialog(wx.Dialog):
    def __init__(self, parent, caption):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)  # | wx.RESIZE_BORDER)
        self.SetTitle(caption)
        self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour('white')
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.options_box = wx.StaticBox(self, wx.ID_ANY, 'Options')
        self.vbox = wx.StaticBoxSizer(self.options_box, wx.VERTICAL)
        self.vbox.AddSpacer(10)

        # Pause input
        self.hbox_pause = wx.BoxSizer(wx.HORIZONTAL)

        self.checkbox_pause = wx.CheckBox(self, label=' Pause between commands: ')
        self.checkbox_pause.SetValue(True)
        self.checkbox_pause.Bind(wx.EVT_CHECKBOX, self.checkbox_pause_pressed)
        self.hbox_pause.Add(self.checkbox_pause, 0, wx.ALIGN_CENTER_VERTICAL)

        self.execute_pause_input = PlaceholderTextCtrl(self, wx.ID_ANY, placeholder='0.2', size=wx.Size(50, -1),
                                                       style=wx.TE_CENTER)
        self.hbox_pause.Add(self.execute_pause_input, 0, wx.ALIGN_CENTER_VERTICAL)

        self.hbox_pause.Add(wx.StaticText(self, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
        self.vbox.Add(self.hbox_pause, 0, wx.EAST | wx.WEST, 10)

        self.vbox.AddSpacer(20)

        # Mouse duration input
        self.hbox_mouse_dur = wx.BoxSizer(wx.HORIZONTAL)

        self.checkbox_mouse_dur = wx.CheckBox(self, label=' Mouse command duration: ')
        self.checkbox_mouse_dur.SetValue(True)
        self.checkbox_mouse_dur.Bind(wx.EVT_CHECKBOX, self.checkbox_mouse_dur_pressed)
        self.hbox_mouse_dur.Add(self.checkbox_mouse_dur, 0, wx.ALIGN_CENTER_VERTICAL)

        self.execute_mouse_dur_input = PlaceholderTextCtrl(self, wx.ID_ANY, placeholder='1', size=wx.Size(50, -1),
                                                           style=wx.TE_CENTER)
        self.hbox_mouse_dur.Add(self.execute_mouse_dur_input, 0, wx.ALIGN_CENTER_VERTICAL)

        self.hbox_mouse_dur.Add(wx.StaticText(self, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
        self.vbox.Add(self.hbox_mouse_dur, 0, wx.EAST | wx.WEST, 10)

        self.vbox.AddSpacer(20)

        # Text type interval duration input
        self.hbox_type_interval = wx.BoxSizer(wx.HORIZONTAL)

        self.checkbox_type_interval = wx.CheckBox(self, label=' Interval between text character outputs: ')
        self.checkbox_type_interval.SetValue(True)
        self.checkbox_type_interval.Bind(wx.EVT_CHECKBOX, self.checkbox_type_interval_pressed)
        self.hbox_type_interval.Add(self.checkbox_type_interval, 0, wx.ALIGN_CENTER_VERTICAL)

        self.execute_type_interval_input = PlaceholderTextCtrl(self, wx.ID_ANY, placeholder='0.05', size=wx.Size(50, -1)
                                                               , style=wx.TE_CENTER)
        self.hbox_type_interval.Add(self.execute_type_interval_input, 0, wx.ALIGN_CENTER_VERTICAL)

        self.hbox_type_interval.Add(wx.StaticText(self, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
        self.vbox.Add(self.hbox_type_interval, 0, wx.EAST | wx.WEST, 10)

        self.vbox.AddSpacer(10)

        self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)

        # self.vbox_outer.Add(wx.StaticLine(self), 0, wx.EXPAND)
        self.vbox_outer.Add(wx.StaticText(self, label='Uncheck option(s) for fastest execution'), 0,
                            wx.ALIGN_RIGHT | wx.NORTH | wx.EAST | wx.WEST, 20)
        self.vbox_outer.Add(self.vbox, 0, wx.EAST | wx.WEST | wx.SOUTH, 20)
        self.vbox_outer.Add(self.btns, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, 15)
        self.SetSizerAndFit(self.vbox_outer)

    def checkbox_pause_pressed(self, event):
        self.execute_pause_input.Enable(self.checkbox_pause.GetValue())

    def checkbox_mouse_dur_pressed(self, event):
        self.execute_mouse_dur_input.Enable(self.checkbox_mouse_dur.GetValue())

    def checkbox_type_interval_pressed(self, event):
        self.execute_type_interval_input.Enable(self.checkbox_type_interval.GetValue())


class SoftwareInfo:
    def __init__(self):
        self.name = 'Aldras'
        self.version = '2020.0.0 Alpha'
        self.copyright = '2020 Aldras'
        self.website = 'http://www.{}.com'.format(self.name.lower())
        self.description = '{} is a simple and intuitive automation tool that can drastically\nimprove the efficiency of processes with repetitive computer tasks.'.format(
            self.name)
        self.advanced_edit_guide_website = '{}/edit-guide'.format(self.website)
        self.advanced_edit_guide_description = self.name + ' is not sensitive capitalization upon ingest,\nplease use whatever convention is most readable for you.'
        self.advanced_edit_guide_command_description = 'Replace the values in the curly brackets { }.'
        self.advanced_edit_guide_commands = {
            '{Left/Right}-mouse {click/press/release} at ({x}, {y})': ['Left-mouse click at (284, 531)',
                                                                       'Simulates mouse click, press, or release'],
            'Type: {text}': ['Type: This report is initiated by John Smith.', 'Simulates text keyboard output'],
            'Sleep {time (seconds)}': ['Sleep 0.5', 'Wait for a specified number of seconds'],
            'Key {key} {tap/press/release} at ({x}, {y})': ['Key Enter Tap',
                                                            'Simulates keyboard key tap, press, or release'],
            'Hotkey {key 1} + {key 2} + {key 3}': [['Hotkey Ctrl + S', 'Hotkey Ctrl + Shift + Left'],
                                                   'Simulates simultaneous keyboard key presses then releases'],
            'Mouse-move to ({x}, {y})': ['Mouse-move to (284, 531)', 'Simulates mouse movement'],
            'Double-click at ({x}, {y})': ['Double-click at (284, 531)', 'Simulates double left click'],
            'Triple-click at ({x}, {y})': ['Triple-click at (284, 531)', 'Simulates triple left click']
        }
        self.commands = ['Mouse button', 'Type', 'Sleep', 'Special key', 'Function key', 'Media key', 'Hotkey',
                         'Mouse-move', 'Double-click', 'Triple-click', 'Scroll']
        self.mouse_buttons = ['Left', 'Right']
        self.mouse_actions = ['Click', 'Press', 'Release']
        self.coord_width = 40
        self.special_keys = ['Backspace', 'Del', 'Enter', 'Tab', 'Left', 'Right', 'Up', 'Down', 'Home', 'End', 'PageUp',
                             'PageDown', 'Space', 'Shift', 'Esc', 'Ctrl', 'Alt', 'Win', 'Command', 'Option',
                             'BrowserBack', 'BrowserForward', 'CapsLock', 'Insert', 'NumLock', 'PrntScrn', 'ScrollLock']
        self.media_keys = ['PlayPause', 'NextTrack', 'PrevTrack', 'VolumeMute', 'VolumeUp', 'VolumeDown']
        self.function_keys = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
        self.alphanum_keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                              'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                              '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<',
                              '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', ' ']
        self.all_keys = [''] + self.special_keys + self.alphanum_keys + self.media_keys + self.alphanum_keys


class EditCommandError(Exception):
    pass


class PlaceholderTextCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        self.default_text = kwargs.pop('placeholder', '')
        wx.TextCtrl.__init__(self, *args, **kwargs)
        self.on_unfocus(None)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_unfocus)

    def on_focus(self, event):
        self.SetForegroundColour(wx.BLACK)
        if self.GetValue() == self.default_text:
            self.SetValue('')

    def on_unfocus(self, event):
        if self.GetValue().strip() == '':
            self.SetValue(self.default_text)
            self.SetForegroundColour(3 * (120,))  # change font color to (r,g,b)


class DeleteCommandsDialog(wx.Dialog):
    def __init__(self, parent, message, caption, choices=None):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))
        self.SetTitle(caption)
        self.SetBackgroundColour('white')
        if choices is None:
            choices = []
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.message = wx.StaticText(self, wx.ID_ANY, message)
        self.check_list_box = wx.CheckListBox(self, wx.ID_ANY, choices=choices)
        self.checkbox = wx.CheckBox(self, wx.ID_ANY, 'Select all')
        self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_CHECKBOX, self.check_all, self.checkbox)

        sizer.Add(self.message, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.check_list_box, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.checkbox, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.btns, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizerAndFit(sizer)

    def get_selections(self):
        return self.check_list_box.GetCheckedItems()

    def check_all(self, event):
        state = self.checkbox.IsChecked()
        for i in range(self.check_list_box.GetCount()):
            self.check_list_box.Check(i, state)


class SaveDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title='{}: Save'.format(parent.software_info.name),
                           style=wx.DEFAULT_DIALOG_STYLE)
        # self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))
        self.SetTitle('Aldras - Save Changes')
        self.SetBackgroundColour('white')
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.message = wx.StaticText(self, wx.ID_ANY,
                                     'Do you want to save changes to \'{}\'?'.format(parent.workflow_name))
        self.message.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))  # change font size
        self.message.SetForegroundColour((35, 75, 160))  # change font color to (r,g,b)
        self.vbox.Add(self.message, 0, wx.ALL, 10)

        self.vbox.AddSpacer(20)
        self.vbox.Add(wx.StaticLine(self), 0, wx.EXPAND)

        self.button_array = wx.StdDialogButtonSizer()
        self.button_array.AddSpacer(100)
        self.save_btn = wx.Button(self, wx.ID_OK, label='Save')
        self.button_array.Add(self.save_btn)
        self.button_array.AddSpacer(5)
        self.save_btn = wx.Button(self, wx.ID_REVERT_TO_SAVED, label='Don\'t Save')
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_no_save)
        self.button_array.Add(self.save_btn)
        self.button_array.AddSpacer(5)
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, label='Cancel')
        self.button_array.Add(self.cancel_btn)

        self.vbox.Add(self.button_array, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizerAndFit(self.vbox)

    def on_no_save(self, event):
        self.EndModal(20)


class AdvancedEditGuide(wx.Dialog):
    def __init__(self, parent):
        self.dirname = ''
        self.software_info = parent.parent.software_info
        self.workflow_name = parent.parent.workflow_name

        wx.Dialog.__init__(self, parent.parent, title='{} Edit Guide'.format(self.software_info.name))

        # setup_frame(self, status_bar=True)

        # create sizers
        self.hbox_outer = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox_inner = wx.BoxSizer(wx.VERTICAL)
        self.vbox_inner.AddStretchSpacer()

        # add encompassing panel
        self.container = wx.Panel(self)

        # add advanced edit guide title
        self.title = wx.StaticText(self.container, label='Advanced Edit Guide')
        self.title.SetFont(wx.Font(wx.FontInfo(18)))  # change font size
        self.title_contrast = 60
        self.title.SetForegroundColour(3 * (self.title_contrast,))  # change font color to (r,g,b)
        self.vbox_inner.Add(self.title)

        self.vbox_inner.AddSpacer(5)

        self.hbox_description = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_description.AddSpacer(5)
        self.description = wx.StaticText(self.container, label=self.software_info.advanced_edit_guide_description)
        self.description.SetToolTip('Feel free to use any capitalization scheme')
        self.hbox_description.Add(self.description)
        self.vbox_inner.Add(self.hbox_description)

        self.vbox_inner.AddSpacer(20)

        # add commands title
        self.command_title = wx.StaticText(self.container, label='Commands')
        self.command_title.SetFont(wx.Font(wx.FontInfo(14)))  # change font size
        self.command_title_contrast = self.title_contrast
        self.command_title.SetForegroundColour(3 * (self.command_title_contrast,))  # change font color to (r,g,b)
        self.vbox_inner.Add(self.command_title)

        self.nmSizer = wx.StaticBoxSizer(wx.StaticBox(self.container, wx.ID_ANY, ''), wx.VERTICAL)
        self.command_description = wx.StaticText(self.container,
                                                 label=self.software_info.advanced_edit_guide_command_description)
        self.command_description.SetFont(wx.Font(10, wx.SWISS, wx.ITALIC, wx.NORMAL))  # change font size
        self.nmSizer.Add(self.command_description, 0, wx.ALIGN_RIGHT)

        self.nmSizer.AddSpacer(25)

        for command, data in self.software_info.advanced_edit_guide_commands.items():
            example = data[0]
            description = data[1]
            self.command = wx.StaticText(self.container, label='  {}     '.format(command))
            self.command.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))  # change font size
            self.command.SetToolTip(description)
            self.nmSizer.Add(self.command)
            self.nmSizer.AddSpacer(5)
            if isinstance(example, list):
                for each_example in example:
                    self.example = wx.StaticText(self.container, label='   {}'.format(each_example))
                    self.example.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))  # change font size
                    self.example.SetForegroundColour(3 * (80,))  # change font color to (r,g,b)
                    self.example.SetToolTip(description)
                    self.nmSizer.Add(self.example)
            else:
                self.example = wx.StaticText(self.container, label='   {}'.format(example))
                self.example.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))  # change font size
                self.example.SetForegroundColour(3 * (80,))  # change font color to (r,g,b)
                self.example.SetToolTip(description)
                self.nmSizer.Add(self.example)

            self.nmSizer.AddSpacer(15)

        self.vbox_inner.Add(self.nmSizer)

        self.vbox_inner.AddSpacer(20)

        self.docs = wx.StaticText(self.container, label='Read the Docs')
        self.docs.SetFont(wx.Font(13, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))  # change font size
        self.docs.SetForegroundColour(3 * (80,))  # change font color to (r,g,b)
        config_status_and_tooltip(self, self.docs, 'More Documentation')
        self.vbox_inner.Add(self.docs, 0, wx.CENTER)

        self.docs_link = wx.adv.HyperlinkCtrl(self.container, wx.ID_ANY,
                                              label='{}.com/docs'.format(self.software_info.name.lower()),
                                              url='{}/docs'.format(self.software_info.website),
                                              style=wx.adv.HL_DEFAULT_STYLE)
        config_status_and_tooltip(self, self.docs_link, 'More Documentation',
                                  tooltip='{}/docs'.format(self.software_info.website))
        self.docs_link.SetFont(wx.Font(11, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))  # change font size
        self.vbox_inner.Add(self.docs_link, 0, wx.CENTER)

        self.vbox_inner.AddSpacer(25)
        self.vbox_inner.AddStretchSpacer()

        self.hbox_outer.AddStretchSpacer()
        self.hbox_outer.Add(self.vbox_inner, 0, wx.CENTER | wx.EXPAND | wx.ALL, 10)
        self.hbox_outer.AddStretchSpacer()

        self.container.SetSizerAndFit(self.hbox_outer)
        self.vbox_inner.SetSizeHints(self)

        self.Show()


class AdvancedEdit(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent,
                           title='{}: Advanced Edit - {}'.format(parent.software_info.name, parent.workflow_name),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour('white')
        self.parent = parent
        self.dirname = ''
        self.adv_edit_guide = None

        # create sizers
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox_inner = wx.BoxSizer(wx.VERTICAL)
        self.hbox_bottom = wx.BoxSizer(wx.HORIZONTAL)

        # add encompassing panel
        self.container = wx.Panel(self)

        # add workflow title
        self.title = wx.StaticText(self.container, label='{}'.format(parent.workflow_name))
        self.title.SetFont(wx.Font(wx.FontInfo(18)))  # change font size
        self.title.SetForegroundColour(3 * (60,))  # change font color to (r,g,b)
        self.vbox_inner.Add(self.title)

        self.vbox_inner.AddSpacer(5)

        self.text_edit = wx.TextCtrl(self.container, value=''.join(parent.lines), style=wx.TE_MULTILINE | wx.EXPAND,
                                     size=(500, 300))

        self.vbox_inner.Add(self.text_edit, 1, wx.EXPAND)

        # ------------------------------------------------------------------------------------------- bottom sizer
        self.vbox_inner.AddSpacer(10)

        self.advanced_edit_guide_btn = wx.Button(self.container, label='Guide')
        self.advanced_edit_guide_btn.Bind(wx.EVT_BUTTON, self.advanced_edit_guide)
        self.hbox_bottom.Add(self.advanced_edit_guide_btn)

        self.hbox_bottom.AddStretchSpacer()

        self.button_array = wx.StdDialogButtonSizer()
        self.ok_btn = wx.Button(self.container, wx.ID_OK, label='OK')
        self.button_array.Add(self.ok_btn)
        self.button_array.AddSpacer(5)
        self.cancel_btn = wx.Button(self.container, wx.ID_CANCEL, label='Cancel')
        self.button_array.Add(self.cancel_btn)
        self.hbox_bottom.Add(self.button_array, 0, wx.ALIGN_RIGHT)

        self.vbox_inner.Add(self.hbox_bottom, 0, wx.EXPAND)

        self.vbox_outer.Add(self.vbox_inner, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.ALL, 10)

        self.container.SetSizer(self.vbox_outer)
        self.vbox_outer.SetSizeHints(self)

        self.Bind(wx.EVT_CLOSE, self.close_window)

    def advanced_edit_guide(self, event):
        if not self.adv_edit_guide or not self.adv_edit_guide.IsShown():  # only if window does not yet exist or is not shown
            self.adv_edit_guide = AdvancedEditGuide(self)
        else:
            self.adv_edit_guide.Raise()  # bring existing edit guide to top

    def close_window(self, event):
        if self.adv_edit_guide:
            self.adv_edit_guide.Close(True)
        self.Destroy()


class EditFrame(wx.Frame):
    def __init__(self, parent):
        t0 = time.time()
        self.dirname = ''
        self.software_info = parent.software_info
        self.workflow_name = parent.workflow_name
        self.workflow_path_name = parent.workflow_path_name
        self.commands = self.software_info.commands
        self.mouse_buttons = self.software_info.mouse_buttons
        self.mouse_actions = self.software_info.mouse_actions
        self.coord_width = self.software_info.coord_width
        self.special_keys = self.software_info.special_keys
        self.media_keys = self.software_info.media_keys
        self.function_keys = self.software_info.function_keys
        self.alphanum_keys = self.software_info.alphanum_keys
        self.all_keys = self.software_info.all_keys

        wx.Frame.__init__(self, parent, title='{}: Edit - {}'.format(self.software_info.name, self.workflow_name))

        setup_frame(self, status_bar=True)

        # set margin
        self.margins = 10

        # create sizers
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.hbox_outer = wx.BoxSizer(wx.HORIZONTAL)

        # add top panel
        self.hbox_top = wx.BoxSizer(wx.HORIZONTAL)

        # add back button
        self.back_btn = wx.Button(self, size=wx.Size(30, -1), label='<')
        self.back_btn.Bind(wx.EVT_BUTTON, lambda event: self.close_window(event, parent, quitall=False))
        config_status_and_tooltip(self, self.back_btn, 'Back to workflow selection')
        self.hbox_top.Add(self.back_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        self.hbox_top.AddSpacer(10)

        # add workflow title
        self.title = wx.StaticText(self, label='{}'.format(self.workflow_name))
        self.title.SetFont(wx.Font(wx.FontInfo(18)))  # change font size
        self.title.SetForegroundColour(3 * (60,))  # change font color to (r,g,b)
        self.hbox_top.Add(self.title, 1, wx.ALIGN_CENTER_VERTICAL)

        self.vbox_outer.Add(self.hbox_top)

        self.vbox_outer.AddSpacer(10)

        # ------------------------------------------------------------------------------------------- bottom sizer

        self.hbox_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.fg_bottom = wx.FlexGridSizer(1, 2, 10, 10)

        # read or create workflow file
        try:
            with open(self.workflow_path_name, 'r') as record_file:
                self.lines = record_file.readlines()
        except FileNotFoundError:  # create file if not found
            with open(self.workflow_path_name, 'w'):
                self.lines = []

        self.lines_as_read = self.lines.copy()

        self.edit_rows = []

        self.vbox_action = wx.BoxSizer(wx.VERTICAL)
        self.hbox_line_mods = wx.BoxSizer(wx.HORIZONTAL)

        # add delete command button
        self.delete_btn = wx.Button(self, label='-', size=(20, -1))
        self.delete_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_open_delete_command_dialog())
        config_status_and_tooltip(self, self.delete_btn, 'Delete commands')
        self.hbox_line_mods.Add(self.delete_btn, 1, wx.EXPAND)

        self.hbox_line_mods.AddSpacer(5)

        # add plus command button
        self.plus_btn = wx.Button(self, label='+', size=(20, -1))
        self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_open_add_command_dialog())
        config_status_and_tooltip(self, self.plus_btn, 'Add commands')
        self.hbox_line_mods.Add(self.plus_btn, 1, wx.ALIGN_RIGHT)

        self.vbox_action.Add(self.hbox_line_mods, 0, wx.EXPAND)

        self.vbox_action.AddSpacer(10)

        # add reorder commands button
        self.reorder_btn = wx.Button(self, label='Reorder')
        self.reorder_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_reorder_dialog())
        config_status_and_tooltip(self, self.reorder_btn, 'Reorder commands')
        self.vbox_action.Add(self.reorder_btn, 0, wx.EXPAND)

        self.vbox_action.AddSpacer(10)

        # add advanced command button
        self.advanced_btn = wx.Button(self, label='Advanced')
        self.advanced_btn.Bind(wx.EVT_BUTTON, lambda event: self.create_advanced_edit_frame())
        config_status_and_tooltip(self, self.advanced_btn, 'Advanced text-based editor')
        self.vbox_action.Add(self.advanced_btn, 0, wx.EXPAND)

        self.vbox_action.AddStretchSpacer()

        # add record command button
        self.record_btn = wx.Button(self, label='Record')
        self.record_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_record())
        config_status_and_tooltip(self, self.record_btn, 'Record workflow actions')
        self.vbox_action.Add(self.record_btn, 0, wx.EXPAND)

        self.vbox_action.AddSpacer(10)

        # add execute command button
        self.execute_btn = wx.Button(self, label='Execute')
        self.execute_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_execute())
        config_status_and_tooltip(self, self.execute_btn, 'Execute workflow actions')
        self.vbox_action.Add(self.execute_btn, 0, wx.ALIGN_BOTTOM | wx.EXPAND)

        self.vbox_edit_container = wx.BoxSizer(wx.VERTICAL)
        self.vbox_edit_container.AddStretchSpacer()

        self.fg_bottom.AddMany([(self.vbox_edit_container, 1, wx.EXPAND), (self.vbox_action, 1, wx.EXPAND)])
        self.fg_bottom.AddGrowableCol(0, 0)
        self.fg_bottom.AddGrowableRow(0, 0)

        self.vbox_outer.Add(self.fg_bottom, 1, wx.EXPAND)

        # add margins and inside sizers
        self.vbox_outer.AddSpacer(5)
        self.hbox_outer.Add(self.vbox_outer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, self.margins)

        self.vbox_edit = None
        self.create_edit_panel()

        self.hbox_outer.SetSizeHints(self)
        self.SetSizer(self.hbox_outer)
        self.Show()
        self.Layout()
        self.Bind(wx.EVT_CLOSE, lambda event: self.close_window(event, parent, quitall=True))
        print(time.time() - t0)

    def add_edit_row(self, row_to_add):
        edit_row_vbox = wx.BoxSizer(wx.VERTICAL)
        edit_row_vbox.Add(row_to_add, 0, wx.EXPAND | wx.NORTH | wx.SOUTH, 5)
        edit_row_vbox.Add(wx.StaticLine(self.edit), 0, wx.EXPAND)
        self.edit_rows.append(edit_row_vbox)

    def create_edit_panel(self):
        self.first_call = True
        if self.vbox_edit:  # if edit panel has been created previously
            self.first_call = False
            for child in self.vbox_edit.GetChildren():
                child.Show(False)
                # child.Destroy()

        self.edit = wx.lib.scrolledpanel.ScrolledPanel(self, style=wx.SIMPLE_BORDER)
        self.edit.SetupScrolling()

        self.vbox_edit = wx.BoxSizer(wx.VERTICAL)
        self.edit.SetSizer(self.vbox_edit)

        self.edit_row_tracker = []

        for index, self.line_orig in enumerate(self.lines):
            self.line_orig = self.line_orig.replace('\n', '')
            self.line = self.line_orig.lower()

            self.hbox_edit = wx.BoxSizer(wx.HORIZONTAL)
            try:
                self.hbox_edit.AddSpacer(5)

                self.move_up = wx.Button(self.edit, size=wx.Size(25, -1), label='▲')
                self.move_up.Bind(wx.EVT_BUTTON,
                                  lambda event, sizer_trap=self.hbox_edit: self.move_command_up(sizer_trap))
                self.hbox_edit.Add(self.move_up, 0, wx.ALIGN_CENTER_VERTICAL)

                self.move_down = wx.Button(self.edit, size=wx.Size(25, -1), label='▼')
                self.move_down.Bind(wx.EVT_BUTTON,
                                    lambda event, sizer_trap=self.hbox_edit: self.move_command_down(sizer_trap))
                self.hbox_edit.Add(self.move_down, 0, wx.ALIGN_CENTER_VERTICAL)

                self.hbox_edit.AddSpacer(5)
                self.line_first_word = self.line.split(' ')[0]

                comment = False
                if not self.line:  # if line is empty
                    self.hbox_edit.Insert(0, 0, 50, 1)
                    self.hbox_edit.Insert(0, 0, 0, 1)

                elif self.line.replace(' ', '')[0] == '#':  # workflow comment`
                    self.vbox_comment = wx.BoxSizer(wx.VERTICAL)
                    self.vbox_comment.Add(wx.StaticLine(self.edit, wx.ID_ANY, size=wx.Size(200, 3)), 0, wx.ALIGN_CENTER)
                    self.vbox_comment.AddSpacer(5)
                    self.vbox_comment.Add(wx.StaticLine(self.edit, wx.ID_ANY), 0, wx.EXPAND)
                    self.vbox_comment.AddSpacer(5)

                    self.hbox_comment = wx.BoxSizer(wx.HORIZONTAL)

                    self.comment_label = wx.StaticText(self.edit, label='#')
                    self.comment_contrast = 100
                    # self.comment_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))  # change font size
                    self.comment_label.SetFont(wx.Font(wx.FontInfo(12)))  # change font size
                    self.comment_label.SetForegroundColour(3 * (self.comment_contrast,))  # change font color to (r,g,b)
                    self.hbox_edit.Add(self.comment_label, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.hbox_edit.AddSpacer(5)

                    self.comment_value = str(self.line_orig).replace('#', '').strip()
                    self.comment = wx.lib.expando.ExpandoTextCtrl(self.edit,
                                                                  value=self.comment_value)  # , size=wx.Size(300, -1))
                    self.comment.SetFont(wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.NORMAL))  # change font size
                    self.comment.SetForegroundColour(3 * (self.comment_contrast,))  # change font color to (r,g,b)
                    self.hbox_edit.Add(self.comment, 3, wx.EXPAND)

                    self.hbox_edit.AddStretchSpacer()
                    self.hbox_edit.AddSpacer(15)

                    self.edit_row_tracker.append(self.hbox_edit)
                    comment = True

                    self.vbox_comment.Add(self.hbox_edit, 1, wx.EXPAND)

                    self.hbox_edit = self.vbox_comment

                elif '-mouse' in self.line_first_word:
                    self.command = wx.ComboBox(self.edit, value='Mouse button', choices=self.commands,
                                               style=wx.CB_READONLY)
                    self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)
                    self.hbox_edit.AddSpacer(10)
                    self.create_mouse_row()

                elif 'type:' in self.line_first_word:
                    self.command = wx.ComboBox(self.edit, value='Type', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)
                    self.hbox_edit.AddSpacer(10)
                    self.text_value = str(self.line_orig).replace('type: ', '').replace('Type: ', '')

                    self.text_to_type = wx.lib.expando.ExpandoTextCtrl(self.edit, value=self.text_value)
                    self.hbox_edit.Add(self.text_to_type, 1, wx.EXPAND)
                    self.hbox_edit.AddSpacer(15)

                elif 'sleep' in self.line_first_word:
                    self.command = wx.ComboBox(self.edit, value='Sleep', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.hbox_edit.AddSpacer(10)

                    self.sleep_time = wx.TextCtrl(self.edit, value=str(self.line.split(' ')[-1]))
                    self.hbox_edit.Add(self.sleep_time, 0, wx.ALIGN_CENTER_VERTICAL)
                    # self.hbox_edit.Add(self.sleep_time, 1, wx.EXPAND)

                elif 'hotkey' in self.line_first_word:
                    self.command = wx.ComboBox(self.edit, value='Hotkey', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.combination = [x.capitalize() for x in
                                        self.line.replace('hotkey', '').replace(' ', '').split('+')]

                    self.hbox_edit.AddSpacer(10)

                    self.counter = 0
                    for self.key in self.combination:
                        self.counter += 1

                        self.hotkey_cb = wx.ComboBox(self.edit, value=str(self.key), choices=self.all_keys,
                                                     style=wx.CB_READONLY)
                        self.hotkey_cb.Bind(wx.EVT_MOUSEWHEEL,
                                            do_nothing)  # disable mouse wheel
                        self.hbox_edit.Add(self.hotkey_cb, 0, wx.ALIGN_CENTER_VERTICAL)

                        if self.counter < len(self.combination):
                            self.label = wx.StaticText(self.edit, label='  +  ')
                            self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                elif 'key' in self.line_first_word:
                    self.key_in = self.line.split(' ')[1]
                    self.key = None  # redefined in self.create_key_combo_box(command) method
                    if self.key_in in [x.lower() for x in self.special_keys]:
                        self.create_key_combo_box('Special key')

                    elif self.key_in in [x.lower() for x in self.function_keys]:
                        self.create_key_combo_box('Function key')

                    elif self.key_in in [x.lower() for x in self.media_keys]:
                        self.create_key_combo_box('Media key')

                    else:
                        raise EditCommandError()

                elif ('mouse' in self.line_first_word) and ('move' in self.line_first_word):
                    self.command = wx.ComboBox(self.edit, value='Mouse-move', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.hbox_edit.AddSpacer(10)
                    self.label = wx.StaticText(self.edit, label='to pt. (  ')
                    self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.create_point_input()

                elif ('double' in self.line) and ('click' in self.line):
                    self.command = wx.ComboBox(self.edit, value='Double-click', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.hbox_edit.AddSpacer(10)
                    self.label = wx.StaticText(self.edit, label='at pt. (  ')
                    self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.create_point_input()

                elif ('triple' in self.line) and ('click' in self.line):
                    self.command = wx.ComboBox(self.edit, value='Triple-click', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.hbox_edit.AddSpacer(10)
                    self.label = wx.StaticText(self.edit, label='at pt. (  ')
                    self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.create_point_input()

                else:
                    raise EditCommandError()

                self.command.Bind(wx.EVT_MOUSEWHEEL, do_nothing)  # disable mouse wheel
                self.command.Bind(wx.EVT_COMBOBOX,
                                  lambda event, sizer_trap=self.hbox_edit: self.combobox_change(sizer_trap, event))

            except EditCommandError as e:
                self.hbox_edit.AddSpacer(10)
                self.unknown_command_message = wx.StaticText(self.edit,
                                                             label='**Unknown command from line: \"{}\"'.format(
                                                                 self.line))
                self.unknown_command_message.SetFont(
                    wx.Font(9, wx.DEFAULT, wx.ITALIC, wx.NORMAL))  # change font size
                self.unknown_command_message.SetForegroundColour(3 * (70,))  # change font color to (r,g,b)
                self.hbox_edit.Add(self.unknown_command_message, 0, wx.ALIGN_CENTER_VERTICAL)

            self.add_edit_row(self.hbox_edit)
            if not comment:
                self.edit_row_tracker.append(self.hbox_edit)
        self.line = ''  # used by other functions to determine if they are called from outside loop

        for self.edit_row in self.edit_rows:
            self.vbox_edit.Add(self.edit_row, 0, wx.EXPAND)

        self.edit.SetSizer(self.vbox_edit)

        self.vbox_edit_container_temp = wx.BoxSizer(wx.VERTICAL)
        self.vbox_edit_container_temp.AddSpacer(0)

        self.hbox_outer.Replace(self.vbox_edit_container, self.vbox_edit_container_temp, recursive=True)

        self.vbox_edit_container = wx.BoxSizer(wx.VERTICAL)
        self.vbox_edit_container.Add(self.edit, 1, wx.EXPAND)
        self.vbox_edit_container.SetMinSize(wx.Size(600, 300))
        self.hbox_outer.Replace(self.vbox_edit_container_temp, self.vbox_edit_container, recursive=True)

    def create_mouse_row(self, sizer=None, coords=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if sizer or 'left' in self.line_first_word:
            self.mouse_button = wx.ComboBox(self.edit, value='Left', choices=self.mouse_buttons,
                                            style=wx.CB_READONLY)
        elif 'right' in self.line_first_word:
            self.mouse_button = wx.ComboBox(self.edit, value='Right', choices=self.mouse_buttons,
                                            style=wx.CB_READONLY)
        else:
            raise EditCommandError('Mouse button not specified.')
        self.mouse_button.Bind(wx.EVT_MOUSEWHEEL, do_nothing)  # disable mouse wheel

        if sizer or 'click' in self.line:
            self.mouse_action = wx.ComboBox(self.edit, value='Click', choices=self.mouse_actions,
                                            style=wx.CB_READONLY)
        elif 'press' in self.line:
            self.mouse_action = wx.ComboBox(self.edit, value='Press', choices=self.mouse_actions,
                                            style=wx.CB_READONLY)
        elif 'release' in self.line:
            self.mouse_action = wx.ComboBox(self.edit, value='Release', choices=self.mouse_actions,
                                            style=wx.CB_READONLY)
        else:
            self.mouse_button.Show(False)
            raise EditCommandError('Mouse action not specified.')
        self.mouse_action.Bind(wx.EVT_MOUSEWHEEL, do_nothing)  # disable mouse wheel

        def add_to_sizer(sizer_to_add_to):
            sizer_to_add_to.Add(self.mouse_button, 0, wx.ALIGN_CENTER_VERTICAL)
            sizer_to_add_to.AddSpacer(10)
            sizer_to_add_to.Add(self.mouse_action, 0, wx.ALIGN_CENTER_VERTICAL)
            sizer_to_add_to.AddSpacer(10)
            sizer_to_add_to.Add(wx.StaticText(self.edit, label='at pt. (  '), 0, wx.ALIGN_CENTER_VERTICAL)

        if not sizer:
            add_to_sizer(self.hbox_edit)
        else:
            add_to_sizer(sizer)

        self.create_point_input(sizer, coords)

    def create_point_input(self, sizer=None, coords=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            x_val = coords_of(self.line)[0]
            y_val = coords_of(self.line)[1]
        else:
            x_val = coords[0]
            y_val = coords[1]

        self.x_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE, size=wx.Size(self.coord_width, -1),
                                   value=str(x_val))  # TODO validator
        self.y_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE, size=wx.Size(self.coord_width, -1),
                                   value=str(y_val))  # TODO validator

        def add_to_sizer(sizer_to_add_to):
            sizer_to_add_to.Add(self.x_coord, 0, wx.ALIGN_CENTER_VERTICAL)
            sizer_to_add_to.Add(wx.StaticText(self.edit, label=' , '), 0, wx.ALIGN_CENTER_VERTICAL)
            sizer_to_add_to.Add(self.y_coord, 0, wx.ALIGN_CENTER_VERTICAL)
            sizer_to_add_to.Add(wx.StaticText(self.edit, label='  )'), 0, wx.ALIGN_CENTER_VERTICAL)

        if not sizer:
            add_to_sizer(self.hbox_edit)
        else:
            add_to_sizer(sizer)

    def refresh_edit_panel(self):
        # hide all vbox_edit children
        for child in self.vbox_edit.GetChildren():
            child.Show(False)

        print('self.edit_rows: {}'.format(self.edit_rows))

        for self.edit_row in self.edit_rows:
            for child in self.edit_row.GetChildren():  # recursively show all row elements
                child.Show(True)

            if not self.edit_row.GetSize()[1] > 0:  # if the row is not added to sizer, add it
                self.vbox_edit.Add(self.edit_row, 0, wx.EXPAND)

        self.Layout()  # update frame

    def create_key_combo_box(self, command):
        self.command = wx.ComboBox(self.edit, value=command, choices=self.commands, style=wx.CB_READONLY)
        # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

        self.hbox_edit.AddSpacer(10)

        if 'Special' in command:
            self.key = wx.ComboBox(self.edit, value=str(self.key_in), choices=self.special_keys,
                                   style=wx.CB_READONLY)
        elif 'Function' in command:
            self.key = wx.ComboBox(self.edit, value=str(self.key_in), choices=self.function_keys,
                                   style=wx.CB_READONLY)
        elif 'Media' in command:
            self.key = wx.ComboBox(self.edit, value=str(self.key_in), choices=self.media_keys,
                                   style=wx.CB_READONLY)

        self.key.Bind(wx.EVT_MOUSEWHEEL, do_nothing)  # disable mouse wheel

        self.hbox_edit.Add(self.key, 0, wx.ALIGN_CENTER_VERTICAL)

    def on_open_delete_command_dialog(self):
        delete_dlg = DeleteCommandsDialog(self, 'Please choose the commands to delete:',
                                          'Delete Commands - {}'.format(self.workflow_name),
                                          self.lines)

        if delete_dlg.ShowModal() == wx.ID_OK:
            indices_to_delete = delete_dlg.get_selections()
            # print('You chose to delete indices' + str(indices_to_delete))
            if indices_to_delete:  # if indices_to_delete is not empty
                for index in sorted(indices_to_delete, reverse=True):
                    del (self.lines[index])
                    del (self.edit_rows[index])
                    del (self.edit_row_tracker[index])
                    self.vbox_edit.Show(index, False)
                    self.vbox_edit.Remove(index)
                self.vbox_edit.Layout()
                self.Layout()

    def on_open_add_command_dialog(self):
        # for testing new rows
        for ii in range(2):
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(wx.StaticText(self.edit, wx.ID_ANY, label='Blah blah blah'), 0, wx.ALIGN_CENTER)
            hbox.AddSpacer(10)
            hbox.Add(wx.ComboBox(self.edit, wx.ID_ANY, choices=['c1', 'c2', 'c3']), 0, wx.ALIGN_CENTER)
            self.add_edit_row(hbox)

        self.refresh_edit_panel()

    def open_reorder_dialog(self):
        items = self.lines
        order = range(len(self.lines))

        reorder_dlg = wx.RearrangeDialog(None, 'The checkboxes do not matter',
                                         'Reorder Commands - {}'.format(self.workflow_name), order,
                                         items)
        reorder_dlg.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))
        reorder_dlg.SetBackgroundColour('white')

        if reorder_dlg.ShowModal() == wx.ID_OK:
            order = reorder_dlg.GetOrder()
            if order != list(range(len(order))):  # only perform operations if order changes
                self.lines = [self.lines[index] for index in order]
                self.edit_rows = [self.edit_rows[index] for index in order]
                self.edit_row_tracker = [self.edit_row_tracker[index] for index in order]
                for index in range(len(self.edit_rows)):
                    if index != order[index]:  # only perform costly GUI operations if indices are different
                        self.vbox_edit.Detach(index)
                        self.vbox_edit.Insert(index, self.edit_rows[index], 0, wx.EXPAND)
                self.Layout()

    def create_advanced_edit_frame(self):
        adv_edit_dlg = AdvancedEdit(self)
        if adv_edit_dlg.ShowModal() == wx.ID_OK:
            if adv_edit_dlg.text_edit.GetValue() != ''.join(self.lines):
                # TODO find way to only add changes rather than compute entire panel again
                self.lines = ['{}\n'.format(x) for x in adv_edit_dlg.text_edit.GetValue().split('\n')]
                self.create_edit_panel()
                self.Layout()

    def move_command_up(self, sizer):
        index = self.edit_row_tracker.index(sizer)
        print('Move up line {}'.format(self.edit_row_tracker.index(sizer)))
        if index > 0:
            self.vbox_edit.Detach(index - 1)
            self.vbox_edit.Insert(index, self.edit_rows[index - 1], 0, wx.EXPAND)
            self.vbox_edit.Layout()
            self.Layout()

            self.lines[index - 1], self.lines[index] = self.lines[index], self.lines[index - 1]
            self.edit_rows[index - 1], self.edit_rows[index] = self.edit_rows[index], self.edit_rows[index - 1]
            self.edit_row_tracker[index - 1], self.edit_row_tracker[index] = self.edit_row_tracker[index], \
                                                                             self.edit_row_tracker[index - 1]
            print('\tchanged to: {}'.format(self.edit_row_tracker.index(sizer)))

    def move_command_down(self, sizer):
        index = self.edit_row_tracker.index(sizer)
        print('Move down line {}'.format(self.edit_row_tracker.index(sizer)))
        try:
            self.vbox_edit.Detach(index)
            self.vbox_edit.Insert(index + 1, self.edit_rows[index], 0, wx.EXPAND)
            self.vbox_edit.Layout()
            self.Layout()

            self.lines[index], self.lines[index + 1] = self.lines[index + 1], self.lines[index]
            self.edit_rows[index], self.edit_rows[index + 1] = self.edit_rows[index + 1], self.edit_rows[index]
            self.edit_row_tracker[index], self.edit_row_tracker[index + 1] = self.edit_row_tracker[index + 1], \
                                                                             self.edit_row_tracker[index]

            print('\tchanged to: {}'.format(self.edit_row_tracker.index(sizer)))
        except (IndexError, wx._core.wxAssertionError):
            pass

    def combobox_change(self, sizer, event):
        # TODO make sure selection is the same (might wipe out parameters)
        # TODO change self.lines in order to trigger save on exit

        index = self.edit_row_tracker.index(sizer)
        new_action = event.GetString()
        line_orig = self.lines[index]
        line = line_orig.lower().replace('\n', '')
        line_first_word = line.split(' ')[0]

        old_coords = (0, 0)
        if '-mouse' in line_first_word:
            old_action = 'Mouse button'
            old_coords = coords_of(line)

        elif 'type:' in line_first_word:
            old_action = 'Type'

        elif 'sleep' in line_first_word:
            old_action = 'Sleep'

        elif 'hotkey' in line_first_word:
            old_action = 'Hotkey'

        elif 'key' in line_first_word:
            key = line.split(' ')[1]
            if key in [x.lower() for x in self.special_keys]:
                old_action = 'Special key'

            elif key in [x.lower() for x in self.function_keys]:
                old_action = 'Function key'

            elif key in [x.lower() for x in self.media_keys]:
                old_action = 'Media key'

        elif ('mouse' in line_first_word) and ('move' in line_first_word):
            old_action = 'Mouse-move'
            old_coords = coords_of(line)

        elif ('double' in line_first_word) and ('click' in line_first_word):
            old_action = 'Double-click'
            old_coords = coords_of(line)

        elif ('triple' in line_first_word) and ('click' in line_first_word):
            old_action = 'Triple-click'
            old_coords = coords_of(line)

        print('Combobox in line {} changed from {} to {}'.format(index, old_action, new_action))
        print(old_action == new_action)

        ###################################################################################
        ###################################################################################

        if old_action == new_action:  # do nothing as not to reset existing parameters
            return

        for ii in reversed(range(6, len(sizer.GetChildren()))):
            sizer.GetChildren()[ii].Show(False)
            sizer.GetChildren()[ii].Destroy()

        if new_action == 'Mouse button':
            self.create_mouse_row(sizer, old_coords)
            self.lines[index] = 'Left-mouse click at (0, 0)'

        self.Layout()

    def on_record(self):
        record_dlg = RecordDialog(self, 'Record - {}'.format(self.workflow_name))

        if record_dlg.ShowModal() == wx.ID_OK:
            dlg_counter = RecordCtrlCounterDialog(self, 'Record - {}'.format(self.workflow_name))
            if dlg_counter.ShowModal() == wx.ID_OK:
                print('complete')

    def on_execute(self):
        execute_dlg = ExecuteDialog(self, 'Execute - {}'.format(self.workflow_name))

        if execute_dlg.ShowModal() == wx.ID_OK:

            if execute_dlg.checkbox_pause.GetValue():
                self.execution_pause = float(execute_dlg.execute_pause_input.GetValue())
            else:
                self.execution_pause = 0.1

            if execute_dlg.checkbox_mouse_dur.GetValue():
                self.execution_mouse_dur = float(execute_dlg.execute_mouse_dur_input.GetValue())
            else:
                self.execution_mouse_dur = 0.1

            if execute_dlg.checkbox_type_interval:
                self.execution_type_intrv = float(execute_dlg.execute_type_interval_input.GetValue())
            else:
                self.execution_type_intrv = 0.02
            dlg_counter = ExecuteCtrlCounterDialog(self, 'Execute - {}'.format(self.workflow_name))
            if dlg_counter.ShowModal() == wx.ID_OK:
                print('complete')

    def close_window(self, event, parent, quitall=False):
        if self.lines_as_read != self.lines:
            save_dialog = SaveDialog(self).ShowModal()
            if save_dialog == wx.ID_OK:
                # write to workflow file
                with open(self.workflow_path_name, 'w') as record_file:
                    for line in self.lines:
                        record_file.write(line)
            elif save_dialog == 20:
                print('don\'t save')
            else:
                print('cancel')
                return

        self.Hide()
        if quitall:
            parent.Close()
        else:
            parent.Show()
            self.Destroy()


class WorkflowFrame(wx.Frame):
    def __init__(self, parent):
        self.dirname = ''
        self.software_info = SoftwareInfo()
        wx.Frame.__init__(self, parent, title='{} Automation'.format(self.software_info.name))

        setup_frame(self)

        self.workflow_directory = 'Workflows/'
        if not os.path.exists(self.workflow_directory):
            os.makedirs(self.workflow_directory)

        self.data_directory = 'data/'
        self.data_directory_recent_workflows = self.data_directory + 'recent_workflows.txt'
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
        try:
            with open(self.data_directory_recent_workflows, 'r') as record_file:
                self.recent_workflows = eliminate_duplicates([line.rstrip('\n') for line in record_file])
                print(self.recent_workflows)
        except FileNotFoundError:  # create file if not found
            with open(self.data_directory_recent_workflows, 'w'):
                self.recent_workflows = []

        # add encompassing panel
        self.container = wx.Panel(self)

        # set margins
        self.margin_y = 25
        self.margin_x = 150

        # set padding
        self.padding_y = 25
        self.padding_x = 100

        # create sizers
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.hbox_outer = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # create north and west margins
        self.vbox_outer.AddSpacer(self.margin_y)
        self.hbox_outer.AddSpacer(self.margin_x)

        # add rescaled logo image
        png = wx.Image('logo.png', wx.BITMAP_TYPE_PNG).Scale(150, 150, quality=wx.IMAGE_QUALITY_HIGH)
        self.logo_img = wx.StaticBitmap(self.container, wx.ID_ANY, wx.Bitmap(png))
        self.vbox.Add(self.logo_img, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program name text
        self.program_name = wx.StaticText(self.container, label='{} Automation'.format(self.software_info.name))
        self.program_name.SetFont(wx.Font(wx.FontInfo(18)))  # change font
        self.program_name.SetForegroundColour(3 * (60,))  # change font color to (r,g,b)
        self.vbox.Add(self.program_name, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program version text
        self.program_version = wx.StaticText(self.container, label='Version {}'.format(self.software_info.version))
        self.program_version.SetFont(wx.Font(wx.FontInfo(10)).Italic())  # change font
        self.program_version.SetForegroundColour(3 * (150,))  # change font color to (r,g,b)
        self.vbox.Add(self.program_version, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.AddSpacer(self.padding_y)

        # add input field for the workflow name
        self.workflow_name_input = PlaceholderTextCtrl(self.container, wx.ID_ANY, placeholder='Workflow',
                                                       size=(200, -1),
                                                       style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_ok, self.workflow_name_input)
        self.vbox.Add(self.workflow_name_input, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.AddSpacer(self.padding_y)

        # add recent workflows
        self.hbox_recent = wx.BoxSizer(wx.HORIZONTAL)
        self.update_recent_workflows()
        self.vbox.Add(self.hbox_recent, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.vbox.AddSpacer(self.padding_y)

        self.hbox_outer.Add(self.vbox)

        # add east margin
        self.hbox_outer.AddSpacer(self.margin_x)

        self.vbox_outer.AddStretchSpacer()
        self.vbox_outer.Add(self.hbox_outer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox_outer.AddStretchSpacer()

        self.button_array = wx.StdDialogButtonSizer()
        self.ok_btn = wx.Button(self.container, label='OK')
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        self.button_array.Add(self.ok_btn)
        self.button_array.AddSpacer(5)
        self.cancel_btn = wx.Button(self.container, label='Exit')
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_exit)
        self.button_array.Add(self.cancel_btn)
        self.vbox_outer.Add(self.button_array, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.container.SetSizer(self.vbox_outer)
        self.vbox_outer.SetSizeHints(self)

        self.ok_btn.SetFocus()
        self.Show()

    def on_exit(self, event):
        self.Close(True)  # close the frame

    def on_ok(self, event):
        if self.workflow_name_input.GetValue() == '':
            # create a message dialog box
            dlg = wx.MessageDialog(self,
                                   'Invalid file name.\nPlease try again.',
                                   'Invalid File Name', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()  # show modal
            dlg.Destroy()  # destroy dialog when finished

        else:
            dlg = wx.MessageDialog(None, 'Please confirm that "{}" is your desired workflow.'.format(
                self.workflow_name_input.GetValue().capitalize()),
                                   '{} Workflow Confirmation'.format(self.software_info.name),
                                   wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()

            if result == wx.ID_YES:
                workflow_name = self.workflow_name_input.GetValue().capitalize()

                self.launch_workflow(workflow_path_name='{}{}.txt'.format(self.workflow_directory, workflow_name))
            else:
                pass  # returns user back to workflow window

    def launch_workflow(self, workflow_path_name):
        workflow_name = workflow_path_name.replace('.txt', '').replace(self.workflow_directory, '')
        print(workflow_path_name)
        print()
        self.workflow_name = workflow_name
        self.workflow_path_name = workflow_path_name

        EditFrame(self)
        self.Hide()

        self.recent_workflows.insert(0, workflow_path_name)
        self.recent_workflows = eliminate_duplicates(self.recent_workflows)
        with open(self.data_directory_recent_workflows, 'w') as record_file:
            for line in self.recent_workflows[0:10]:
                record_file.write('{}\n'.format(line))

        self.update_recent_workflows()
        self.hbox_recent.Layout()
        self.container.SetSizerAndFit(self.vbox_outer)
        self.Fit()

    def update_recent_workflows(self):
        self.hbox_recent.ShowItems(show=False)
        self.hbox_recent.Clear(delete_windows=True)
        # print(self.hbox_recent.GetChildren())

        self.recent_workflow_btns = [None] * len(self.recent_workflows[0:3])
        for workflow_path_name in self.recent_workflows[0:3]:
            # print(workflow_path_name)
            workflow_name = workflow_path_name.replace('.txt', '').replace(self.workflow_directory, '')
            self.recent_workflow_btn = wx.Button(self.container, wx.ID_ANY, label=workflow_name)
            self.recent_workflow_btn.Bind(wx.EVT_BUTTON,
                                          lambda event, workflow_path_trap=workflow_path_name: self.launch_workflow(
                                              workflow_path_trap))
            self.hbox_recent.Add(self.recent_workflow_btn)

        self.hbox_recent.ShowItems(show=True)

    # def on_open(self, e):
    #     """ Open a file"""
    #     dlg = wx.FileDialog(self, 'Choose a file', self.dirname, '', '*.*', wx.FD_OPEN)
    #     if dlg.ShowModal() == wx.ID_OK:
    #         self.filename = dlg.GetFilename()
    #         self.dirname = dlg.GetDirectory()
    #         f = open(os.path.join(self.dirname, self.filename), 'r')
    #         self.workflow_name_input.SetValue(f.read())
    #         f.close()
    #     dlg.Destroy()
    #########################################################################
    # OR
    #########################################################################
    # directory selector
    # dlg = wx.DirDialog(None, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
    # if dlg.ShowModal() == wx.ID_OK:
    #     fdir = dlg.GetPath() + "/"
    #     dlg.SetPath(fdir)
    #     print('You selected: %s\n' % dlg.GetPath())
    # dlg.Destroy()


def main():
    app = wx.App(False)
    WorkflowFrame(None)
    app.MainLoop()


if __name__ == '__main__':
    main()
