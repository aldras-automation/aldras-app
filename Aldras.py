import ctypes
import math
import os
import re
import threading
import time
import webbrowser
import string
from screeninfo import get_monitors
import pandas as pd
import pyautogui as pyauto
import wx
import wx.adv
import wx.lib.expando
import wx.lib.scrolledpanel
import wx.grid
from pynput import keyboard, mouse
from platform import system as system_platform
import numpy as np
import clipboard


# TODO comments
# TODO implement fading shade color of recently modified command
# TODO implement encrypted file storage for preferences and other data (resolution)
# TODO error codes with random generation for beta testing bug fixes
# TODO image for recording, executing, and stopping (animation)
# TODO investigate compartmentalization for better organization
# TODO alternate row shading (edit frame)
# TODO control key validation
# TODO re-runs
# TODO investigate compilation speed increases (numba, cpython, pypy)
# TODO investigate speed optimization by converting lists to sets used for 'in' comparisons
# TODO investigate speed optimization with multiprocessing
# TODO premium feature separation (any workflow destination)
# TODO add Mac specific instructions (control --> command key) possibly ESC key?


def eliminate_duplicates(list_with_duplicates):
    """Eliminates duplicates from list"""
    seen = set()
    seen_add = seen.add
    return [x for x in list_with_duplicates if not (x in seen or seen_add(x))]


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
    floats = re.findall(r'[-+]?\d*\.\d+|\d+', input_string)
    if not floats:
        output = float(0)
    elif len(floats) > 1:
        output = [float(indiv_float) for indiv_float in floats]
    else:
        output = float(floats[0])

    return output


def variable_name_in(input_string):
    """Return variable in string between {{~ and ~}} syntax"""
    variables = re.findall(r'(?<={{~)(.*?)(?=~}})', input_string)
    if len(variables) == 1:
        return variables[0]
    else:
        raise ValueError


def assignment_variable_value_in(input_string):
    """Return string after equals sign"""
    return '='.join(input_string.split('=')[1:])


def conditional_operation_in(input_string, operations):
    """Return matching operation between ~}} and ~ syntax"""
    operation_in = input_string.split('~')[2].replace('}}', '').lower()
    matching_operations_in = [element for element in operations if element.lower() in operation_in]
    if len(matching_operations_in) == 0:
        raise ValueError('Invalid conditional operation')
    return matching_operations_in[0]


def conditional_comparison_in(input_string):
    """Return matching operation between ~ and ~ syntax after variable {{~var~}}"""
    return input_string.replace('{{~', '').replace('~}}', '').split('~')[1]


def matching_widget_in_edit_row(sizer, name):
    matching_widgets = [child.GetWindow() for child in sizer.GetChildren() if child.GetWindow() and child.GetWindow().GetName() == name]

    if not matching_widgets:
        return ValueError(f'No matching widgets with name \'{name}\'')
    elif len(matching_widgets) == 1:
        return matching_widgets[0]
    else:
        raise ValueError(f'Multiple matching widgets with name \'{name}\'')


def setup_frame(self, status_bar=False):
    """Setup standardized frame characteristics including file menu and status bar."""

    def on_about(_):
        """Creates about dialog."""

        class AboutDialog(wx.Dialog):
            def __init__(self, parent, caption):
                wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)  # | wx.RESIZE_BORDER)
                self.SetTitle(caption)
                self.SetBackgroundColour('white')
                self.parent = parent
                self.SetIcon(wx.Icon(self.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                self.vbox = wx.FlexGridSizer(2, 1, 10, 10)

                self.vbox_top = wx.BoxSizer(wx.VERTICAL)

                self.hbox_logo_name_version = wx.BoxSizer(wx.HORIZONTAL)

                # add rescaled logo image
                png = wx.Image(self.parent.software_info.png, wx.BITMAP_TYPE_PNG).Scale(150, 150,
                                                                                        quality=wx.IMAGE_QUALITY_HIGH)
                self.logo_img = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(png))
                self.hbox_logo_name_version.Add(self.logo_img, 0, wx.ALIGN_CENTER_VERTICAL)
                self.vbox_name_version = wx.BoxSizer(wx.VERTICAL)

                # add program name text
                self.program_name = wx.StaticText(self, label=f'{self.parent.software_info.name} Automation')
                change_font(self.program_name, size=18, color=3 * (20,))
                self.vbox_name_version.Add(self.program_name, 0, wx.ALIGN_CENTER_HORIZONTAL)

                # add program version text
                self.program_version = wx.StaticText(self, label=f'Version {self.parent.software_info.version}')
                change_font(self.program_version, size=10, style=wx.ITALIC, color=3 * (80,))
                self.vbox_name_version.Add(self.program_version, 0, wx.ALIGN_CENTER_HORIZONTAL)

                self.hbox_logo_name_version.Add(self.vbox_name_version, 0, wx.ALIGN_CENTER_VERTICAL)
                self.vbox_top.Add(self.hbox_logo_name_version, 0, wx.ALIGN_CENTER_HORIZONTAL)

                # add program description text
                self.program_description = wx.StaticText(self, label=self.parent.software_info.description)
                change_font(self.program_description, size=10, color=3 * (40,))
                self.vbox_top.Add(self.program_description, 0, wx.ALIGN_CENTER_HORIZONTAL)

                # add program link
                self.program_link = wx.adv.HyperlinkCtrl(self, label=self.parent.software_info.website,
                                                         url=self.parent.software_info.website)
                self.vbox_top.Add(self.program_link, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH, 15)

                # add copyright
                self.program_copyright = wx.StaticText(self, label=f'© {self.parent.software_info.copyright}')
                self.vbox_top.Add(self.program_copyright, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH, 10)

                self.hbox_btns = wx.BoxSizer(wx.HORIZONTAL)

                def launch_license(_):
                    webbrowser.open_new_tab(self.parent.software_info.website)

                def launch_privacy(_):
                    webbrowser.open_new_tab(self.parent.software_info.website)

                # add license button
                self.license_btn = wx.Button(self, label='License')
                self.license_btn.SetFocus()
                self.license_btn.Bind(wx.EVT_BUTTON, launch_license)
                self.hbox_btns.Add(self.license_btn)

                self.hbox_btns.AddStretchSpacer()
                self.hbox_btns.AddSpacer(5)
                self.hbox_btns.AddStretchSpacer()

                # add privacy statement button
                self.privacy_btn = wx.Button(self, label='Privacy Statement')
                self.privacy_btn.Bind(wx.EVT_BUTTON, launch_privacy)
                self.hbox_btns.Add(self.privacy_btn)

                self.vbox.AddMany([(self.vbox_top, 0, wx.EXPAND | wx.NORTH | wx.EAST | wx.WEST, 40),
                                   (self.hbox_btns, 0, wx.EXPAND | wx.NORTH, 20)])

                self.vbox_outer.Add(self.vbox, 0, wx.ALL, 5)
                self.SetSizerAndFit(self.vbox_outer)
                self.Center()

        about_dlg = AboutDialog(self, f'About {self.software_info.name}')
        about_dlg.ShowModal()

    def on_mouse_monitor(_):
        global mouse_monitor_frame
        if not mouse_monitor_frame:
            class MouseMonitorFrame(wx.Frame):
                """Main frame to select workflow."""

                def __init__(self, parent):
                    wx.Frame.__init__(self, parent, title=f'{parent.software_info.name} Mouse Monitor')
                    self.SetBackgroundColour('white')
                    self.parent = parent
                    self.SetIcon(wx.Icon(self.parent.software_info.icon, wx.BITMAP_TYPE_ICO))  # assign icon
                    self.Bind(wx.EVT_CLOSE, self.close_window)

                    self.padding = 5
                    self.margin = 40

                    self.menubar = wx.MenuBar()
                    self.viewMenu = wx.Menu()
                    self.cb_click_freeze = self.viewMenu.Append(wx.ID_ANY, 'Freeze mouse click positions',
                                                                kind=wx.ITEM_CHECK)
                    self.cb_ctrl_freeze = self.viewMenu.Append(wx.ID_ANY, 'Freeze positions when CTRL tapped',
                                                               kind=wx.ITEM_CHECK)

                    self.viewMenu.Check(self.cb_click_freeze.GetId(), True)
                    self.viewMenu.Check(self.cb_ctrl_freeze.GetId(), True)

                    self.menubar.Append(self.viewMenu, '&Freeze')
                    self.SetMenuBar(self.menubar)

                    # create sizers
                    self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                    self.flex_grid = wx.FlexGridSizer(1, 2, 10, 10)
                    self.vbox_live = wx.BoxSizer(wx.VERTICAL)

                    # add rescaled mouse logo image
                    png = wx.Image('data/aldras_mouse.png', wx.BITMAP_TYPE_PNG).Scale(80, 80,
                                                                                      quality=wx.IMAGE_QUALITY_HIGH)
                    self.logo_img = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(png))
                    self.vbox_live.Add(self.logo_img, 0, wx.ALIGN_CENTER_HORIZONTAL)

                    # add coordinate text
                    self.current_coords = wx.StaticText(self, label=f'{display_size}')
                    change_font(self.current_coords, size=22, color=3 * (60,))
                    self.vbox_live.Add(self.current_coords, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH, 4 * self.padding)

                    # add coordinate label
                    self.coords_label_spacer = ' ' * len(str(display_size))
                    self.coords_label = wx.StaticText(self, label=f'x{self.coords_label_spacer}y')
                    change_font(self.coords_label, size=14, color=3 * (100,))
                    self.vbox_live.Add(self.coords_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH, 2 * self.padding)

                    # ----------------------------------------------------------------------------------- freeze history
                    self.vbox_history = wx.BoxSizer(wx.VERTICAL)

                    self.recent_title = wx.StaticText(self, label='History')
                    change_font(self.recent_title, size=11, style=wx.ITALIC)
                    self.vbox_history.Add(self.recent_title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP | wx.SOUTH,
                                          self.padding)

                    self.freeze_panel = wx.Panel(self)

                    self.vbox_freeze = wx.BoxSizer(wx.VERTICAL)
                    self.freeze_panel.SetSizer(self.vbox_freeze)

                    # set minimum size of freeze panel before any freezes triggered
                    hbox_freeze_temp = wx.BoxSizer(wx.HORIZONTAL)

                    freeze_coords_temp = wx.StaticText(self.freeze_panel, label=f'{display_size}')
                    change_font(freeze_coords_temp, size=11)
                    hbox_freeze_temp.Add(freeze_coords_temp, 0, wx.WEST, self.padding)

                    freeze_type_temp = wx.StaticText(self.freeze_panel, label='click')
                    change_font(freeze_type_temp, size=11, style=wx.ITALIC)
                    hbox_freeze_temp.Add(freeze_type_temp, 0, wx.EAST, 5)

                    self.freeze_panel.SetMinSize(wx.Size(round(1.5 * hbox_freeze_temp.GetMinSize()[0]), -1))
                    hbox_freeze_temp.Clear(delete_windows=True)

                    self.vbox_history.Add(self.freeze_panel, 1, wx.EXPAND)

                    self.flex_grid.AddMany(
                        [(self.vbox_live, 1, wx.EXPAND | wx.EAST, self.margin), (self.vbox_history, 1, wx.EXPAND)])
                    self.flex_grid.AddGrowableCol(0, 2)
                    self.flex_grid.AddGrowableCol(1, 1)

                    self.vbox_outer.AddStretchSpacer()
                    self.vbox_outer.Add(self.flex_grid, 0, wx.EXPAND | wx.ALL, self.margin)
                    self.vbox_outer.AddStretchSpacer()

                    self.SetSizerAndFit(self.vbox_outer)
                    self.vbox_live.SetMinSize(
                        self.vbox_live.GetSize())  # prevent resizing of window as length of live coordinate changes

                    self.Center()
                    self.Show()

                    global mouse_monitor_open
                    mouse_monitor_open = True

                    # noinspection PyGlobalUndefined
                    class MonitorThread(threading.Thread):
                        def __init__(self, thread_parent):
                            """Init Worker Thread Class."""
                            threading.Thread.__init__(self, daemon=True)
                            self.parent = thread_parent

                        def run(self):
                            """Run worker thread."""
                            self.prev_output_len = 0
                            self.freezes = []

                            def update_monitor(x, y, freeze=''):
                                if x < 0:
                                    x = 0
                                if y < 0:
                                    y = 0
                                output = f'({x}, {y})'

                                self.parent.current_coords.SetLabel(output)  # set current coordinates
                                if len(
                                        output) != self.prev_output_len:  # change 'x' and 'y' label spacing if length is different
                                    self.prev_output_len = len(output)
                                    self.parent.coords_label.SetLabel(f'x{" " * len(output)}y')
                                    self.parent.Layout()

                                if freeze:
                                    hbox_freeze = wx.BoxSizer(wx.HORIZONTAL)

                                    freeze_coords = wx.StaticText(self.parent.freeze_panel, label=output)
                                    change_font(freeze_coords, size=11)
                                    hbox_freeze.Add(freeze_coords, 1, wx.ALIGN_LEFT | wx.WEST, 5)

                                    freeze_type = wx.StaticText(self.parent.freeze_panel, label=freeze)
                                    change_font(freeze_type, size=11, style=wx.ITALIC, color=3 * (60,))
                                    hbox_freeze.Add(freeze_type, 0, wx.EAST, 5)

                                    self.parent.vbox_freeze.Insert(0, hbox_freeze, 0, wx.EXPAND | wx.NORTH | wx.SOUTH,
                                                                   5)

                                    num_freezes = 5
                                    if len(self.parent.vbox_freeze.GetChildren()) > num_freezes:
                                        self.parent.vbox_freeze.Remove(
                                            self.parent.vbox_freeze.GetChildren()[num_freezes].GetSizer())

                                    for index, freeze_sizeritem in enumerate(self.parent.vbox_freeze.GetChildren()):
                                        freeze_sizer_sizeritems = freeze_sizeritem.GetSizer().GetChildren()
                                        for static_text_sizeritem in freeze_sizer_sizeritems:
                                            static_text = static_text_sizeritem.GetWindow()
                                            static_text.SetForegroundColour(3 * (index * 50,))

                                    self.parent.Layout()
                                    self.parent.Update()

                            def on_move(x, y):
                                """Process click for mouse listener for MonitorThread instances."""
                                update_monitor(x, y)

                            def on_click(x, y, button, pressed):
                                """Process click for mouse listener for MonitorThread instances."""
                                if pressed and self.parent.cb_click_freeze.IsChecked():
                                    self.freezes.append([str((x, y)), 'CLICK'])
                                    update_monitor(x, y, freeze='click')

                            self.mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
                            self.mouse_listener.start()

                            def on_key_press(key):
                                """Process keystroke press for keyboard listener for MonitorThread instances."""
                                if 'ctrl' in str(key) and self.parent.cb_ctrl_freeze.IsChecked():
                                    x, y = pyauto.position().x, pyauto.position().y
                                    self.freezes.append([str((x, y)), 'R-CTRL'])
                                    update_monitor(x, y, freeze='ctrl')

                            self.key_listener = keyboard.Listener(on_release=on_key_press)
                            self.key_listener.start()

                        def abort(self):
                            """Abort worker thread."""
                            # Method for use by main thread to signal an abort
                            self.mouse_listener.stop()
                            self.key_listener.stop()

                    self.monitor_thread = MonitorThread(self)
                    self.monitor_thread.start()

                def close_window(self, close_event):
                    self.monitor_thread.abort()
                    self.parent.Layout()
                    close_event.Skip()

            mouse_monitor_frame = MouseMonitorFrame(self)
        else:
            mouse_monitor_frame.Raise()

    def on_exit(_):
        self.Close(True)

    if status_bar:
        self.CreateStatusBar()

    # setting up the file menu
    file_menu = wx.Menu()
    menu_about = file_menu.Append(wx.ID_ABOUT, 'About', f' Information about {self.software_info.name}')
    self.Bind(wx.EVT_MENU, on_about, menu_about)
    menu_mouse_monitor = file_menu.Append(wx.ID_ANY, 'Mouse monitor',
                                          f' {self.software_info.name} mouse monitoring tool')
    self.Bind(wx.EVT_MENU, on_mouse_monitor, menu_mouse_monitor)
    menu_exit = file_menu.Append(wx.ID_EXIT, 'Exit', f' Exit {self.software_info.name}')
    self.Bind(wx.EVT_MENU, on_exit, menu_exit)

    # Menu for open option (future)
    # menu_open = file_menu.Append(wx.ID_OPEN, 'Open', ' Open a file to edit')
    # self.Bind(wx.EVT_MENU, self.OnOpen, menu_open)

    # create menu bar
    menu_bar = wx.MenuBar()
    menu_bar.Append(file_menu, 'File')  # Adding the file menu to the menu bar
    self.SetMenuBar(menu_bar)  # adding the menu bar to the Frame)

    self.SetIcon(wx.Icon(self.software_info.icon, wx.BITMAP_TYPE_ICO))  # assign icon

    self.SetBackgroundColour('white')  # set background color


def change_font(widget, size=None, family=None, style=None, weight=None, color=None):
    # set default parameters
    size = size if size is not None else 9
    family = family if family is not None else wx.DEFAULT
    style = style if style is not None else wx.NORMAL
    weight = weight if weight is not None else wx.NORMAL

    widget.SetFont(wx.Font(size, family, style, weight))

    if color is not None:
        widget.SetForegroundColour(color)


def non_flickering_static_text(parent, label):
    static_text = wx.StaticText(parent, wx.ID_ANY, label)
    static_text.Bind(wx.EVT_ERASE_BACKGROUND, lambda _: None)
    return static_text


# noinspection PyTypeChecker
def config_status_and_tooltip(parent, obj_to_config, status='', tooltip=''):
    """
    Configure status bar and tooltip for object.

    Parameters:
        parent (wx.Frame or wx.Dialog): The parent frame for which the status and tool tip should be configured.
        obj_to_config (wx.Widget): The widget for which the status and tool tip should be configured.
        status (str): The string that should be displayed for the status.
        tooltip (bool or str): 'True' should be passed if the tooltip should be configured with the status string. Another string should be passed if the tooltip should be configured with another string.
    """

    def update_status_bar(parent_win, status_to_update, event):
        parent_win.StatusBar.SetStatusText(status_to_update)
        event.Skip()

    def clear_status_bar(parent_win, event):
        parent_win.StatusBar.SetStatusText('')
        event.Skip()

    if tooltip:
        obj_to_config.SetToolTip(tooltip)

    if status:
        obj_to_config.Bind(wx.EVT_ENTER_WINDOW, lambda event: update_status_bar(parent, f'   {status}', event))
        obj_to_config.Bind(wx.EVT_LEAVE_WINDOW, lambda event: clear_status_bar(parent, event))


def textctrl_tab_trigger_nav(event):
    """Function to process tab keypresses and trigger panel navigation."""
    if event.GetKeyCode() == wx.WXK_TAB:
        event.EventObject.Navigate()
    event.Skip()


class ResultEvent(wx.PyEvent):
    """Event to carry result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(int(EVT_RESULT_ID))
        self.data = data


# noinspection PyGlobalUndefined
class ListenerThread(threading.Thread):
    def __init__(self, parent, listen_to_key=True, listen_to_mouse=True, record=False):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self, daemon=True)
        self.parent = parent
        self.listen_to_key = listen_to_key
        self.listen_to_mouse = listen_to_mouse
        self.record = record
        self.in_action = False
        if self.record:
            global recording_lines
            recording_lines = []
        try:
            self.ctrl_keys_df = pd.read_csv(
                f'{self.parent.parent.parent.software_info.data_directory}ctrl_keys_ref.csv',
                names=['Translation', 'Code'])  # reference for all ctrl hotkeys (registered as separate key)
            self.ctrl_keys_df = self.ctrl_keys_df.set_index('Code')
        except FileNotFoundError as _:
            print('FileNotFoundError: [Errno 2] File ctrl_keys_ref.csv does not exist: \'ctrl_keys_ref.csv\'')
            raise FileNotFoundError

    def run(self):
        """Run worker thread."""
        global ctrls
        ctrls = 0

        def output_to_file_bkup(output='', end='\n'):
            """Print string and write to file."""

            # TODO function still needed?

            try:
                global recording_lines
                recording_lines.append(output)
                print(recording_lines)
            except NameError:
                pass

            # output = (output + end)
            # print(output)

            # Will add back when recording is enabled
            # with open(workflow_name+'_bkup.txt', 'a') as record_file:
            #     record_file.write(''.join(output))
            # print(output, end='')

        if self.listen_to_key:

            def on_press_recording(key):
                """Process keystroke press for keyboard listener for ListenerThread instances."""
                global capslock
                global ctrls
                # global self.in_action
                output = str(key).strip('\'').lower()
                coords = ''
                if self.in_action:
                    if output == 'key.caps_lock':  # if capslock pressed, swap capslock state
                        capslock = not capslock
                    if output == 'key.ctrl_l':  # if left ctrl is pressed, record current mouse position
                        coords = tuple(pyauto.position())
                    if not output.startswith('key'):  # i.e., if output is alphanumeric
                        if capslock:
                            output = output.swapcase()
                    if (output.startswith('\\') and output != '\\\\') or (
                            output.startswith('<') and output.endswith('>')):  # substituted ctrl+_key_ value
                        output = self.ctrl_keys_df['Translation'][output.replace('<', '').replace('>', '')]
                    if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
                        output_to_file_bkup('Key \\ press')
                        output = ''
                    if output == '\"\'\"':
                        output = '\''
                    if (not output.startswith('key.ctrl_r')) and (
                            not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
                        if 'key.' in output:
                            output = output.replace('key.', '')
                        output = f'Key {output} press'
                        if coords:
                            output = f'{output} at {coords}'
                        output_to_file_bkup(output)
                if 'key.ctrl_r' in output:
                    ctrls += 1
                    print(f'{ctrls}  ', end='')
                    event_message = 'Error!'
                    if not self.in_action:
                        if ctrls == 1:
                            event_message = 'Action in 3'
                        elif ctrls == 2:
                            event_message = 'Action in 3 2'
                        elif ctrls == 3:
                            event_message = 'Action'
                    elif self.in_action:
                        if ctrls == 1:
                            event_message = 'Stopping in 3'
                        elif ctrls == 2:
                            event_message = 'Stopping in 3 2'
                        elif ctrls == 3:
                            event_message = 'Completed!'

                    wx.PostEvent(self.parent, ResultEvent(event_message))

                    # TODO revisit and optimize
                    if ctrls >= 3:
                        ctrls = 0
                        self.in_action = not self.in_action

            def on_release_recording(key):
                """Process keystroke release for keyboard listener for ListenerThread instances."""
                # TODO revisit and optimize
                global capslock
                global ctrls
                # global self.in_action
                output = str(key).strip('\'').lower()
                coords = ''
                if self.in_action:
                    if output == 'key.ctrl_l':  # if left ctrl is pressed, record current mouse position
                        coords = tuple(pyauto.position())
                    if not output.startswith('key'):  # i.e., if output is alphanumeric
                        if capslock:
                            output = output.swapcase()
                    if (output.startswith('\\') and output != '\\\\') or (
                            output.startswith('<') and output.endswith('>')):  # substituted ctrl+_key_ value
                        output = self.ctrl_keys_df['Translation'][output.replace('<', '').replace('>', '')]
                    if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
                        output_to_file_bkup('Key \\ release')
                        output = ''
                    if output == '\"\'\"':
                        output = '\''
                    if (not output.startswith('key.ctrl_r')) and (
                            not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
                        if 'key.' in output:
                            output = output.replace('key.', '')
                        output = f'Key {output} release'
                        if coords:
                            output = f'{output} at {coords}'
                        output_to_file_bkup(output)

            self.key_listener = keyboard.Listener(on_press=on_press_recording, on_release=on_release_recording)
            self.key_listener.start()

        if self.listen_to_mouse:
            def on_click_recording(x, y, button, pressed):
                """Process click for mouse listener for ListenerThread instances."""
                if self.in_action:
                    button = str(button).replace('Button.', '').capitalize()
                    output_to_file_bkup(f'{button}-mouse {"press" if pressed else "release"} at {(x, y)}')

            self.mouse_listener = mouse.Listener(on_click=on_click_recording)
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

    @staticmethod
    def compile_recording():
        global recording_lines
        lines = recording_lines
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


class PlaceholderTextCtrl(wx.TextCtrl):
    """Placeholder text ctrl."""

    def __init__(self, *args, **kwargs):
        self.default_text = kwargs.pop('placeholder', '')  # remove default text parameter
        wx.TextCtrl.__init__(self, *args, **kwargs)
        self.on_unfocus(None)
        self.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_unfocus)

    def on_focus(self, _):
        self.SetForegroundColour(wx.BLACK)
        if self.GetValue() == self.default_text:
            self.SetValue('')

    def on_unfocus(self, _):
        if self.GetValue().strip() == '':
            self.SetValue(self.default_text)
            self.SetForegroundColour(3 * (120,))


class CustomGrid(wx.grid.Grid):
    def __init__(self, parent, table_size, style=wx.WANTS_CHARS, can_change_num_rows=True, can_change_num_cols=True):
        wx.grid.Grid.__init__(self, parent, style=style)
        self.parent = parent
        self.CreateGrid(*table_size)
        self.editor = wx.grid.GridCellAutoWrapStringEditor()
        self.SetDefaultEditor(self.editor)
        self.SetDefaultRenderer(wx.grid.GridCellAutoWrapStringRenderer())

        self.can_change_num_rows = can_change_num_rows
        self.can_change_num_cols = can_change_num_cols

        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, lambda event: self.resize_rows())  # when selected cell changes, autoresize the rows and layout the parent window
        self.Bind(wx.EVT_CHAR_HOOK, self.on_frame_char_hook)  # when key is pressed

    def resize_rows(self):
        self.AutoSizeRows()
        self.parent.GetParent().Layout()

    def on_frame_char_hook(self, event):
        """Process key presses"""

        if event.ControlDown() and (event.GetKeyCode() == wx.WXK_BACK or event.GetKeyCode() == wx.WXK_DELETE):
            self.clear_cells()

        elif event.ControlDown() and event.GetKeyCode() == 86:  # if CTRL+v
            self.paste_clipboard()

        elif event.ControlDown() and event.GetKeyCode() == 67:  # if CTRL+c
            # TODO process copy events
            pass

        else:
            event.Skip()

    def clear_cells(self):
        """
        Clear selected cells if CTRL+Backspace or CTRL+Del are

        There are three ways cells can be selected:
        1. Multiple cells were click-selected (GetSelectedCells)
        2. Multiple cells were drag or arrow-key selected (GetSelectionBlocks)
        3. A single cell only is selected (CursorRow/Col)
        """

        if self.GetSelectedCells():  # multiple cells click selected
            for cell_coords in self.GetSelectedCells():
                self.SetCellValue(cell_coords[0], cell_coords[1], '')

        else:
            try:  # multiple cells drag or arrow-key selected
                selection_coords = next(
                    self.GetSelectedBlocks().__iter__()).Get()  # get (row1, col1, row2, col2) of cells selection

                for row_index in range(selection_coords[0], selection_coords[2] + 1):
                    for col_index in range(selection_coords[1], selection_coords[3] + 1):
                        self.SetCellValue(row_index, col_index, '')

            except StopIteration:  # single cell selected
                self.SetCellValue(self.GetGridCursorRow(), self.GetGridCursorCol(), '')

        self.resize_rows()

    def clear_all_cells(self):
        self.ClearGrid()
        self.resize_rows()

    def paste_clipboard(self):
        clipboard_text = clipboard.paste()
        excel_list = clipboard_text.split('\r\n')  # split rows
        excel_list = [row.split('\t') for row in excel_list]  # split columns
        try:
            excel_list.remove([''])  # appears sometimes when dealing with copied excel text
        except ValueError:
            pass
        excel_array = np.array(excel_list)

        # get location of currently selected cell to paste at that location
        row_selection = self.GetGridCursorRow()
        col_selection = self.GetGridCursorCol()

        # loop through grid indices as determined by the clipboard excel array size
        for row_index in range(row_selection, row_selection+excel_array.shape[0]):
            if row_index >= self.GetNumberRows():
                if not self.can_change_num_rows:
                    break  # stop if cannot change the number of rows
                else:
                    self.AppendRows()

            for column_index in range(col_selection, col_selection+excel_array.shape[1]):
                if column_index >= self.GetNumberCols():
                    if not self.can_change_num_cols:
                        break  # stop if cannot change the number of rows
                    else:
                        self.AppendCols()

                self.SetCellValue(row_index, column_index, excel_array[row_index-row_selection, column_index-col_selection])

        self.resize_rows()


class EditFrame(wx.Frame):
    """Frame to edit specific workflow."""

    def __init__(self, parent, lines):
        t0 = time.time()
        self.software_info = parent.software_info
        self.workflow_name = parent.workflow_name
        self.workflow_name_when_launched = parent.workflow_name
        self.parent = parent
        self.lines = lines
        self.lines_when_launched = self.lines.copy()  # used for comparison when closing
        self.variables = dict()
        wx.Frame.__init__(self, parent, title=f'{self.software_info.name}: Edit - {self.workflow_name}')
        setup_frame(self, status_bar=True)

        # set parameters
        self.margin = 10
        self.num_hotkeys = 3  # TODO to be set by preferences
        self.default_coords = (10, 10)
        self.loading_dlg_line_thresh = 25
        self.conditional_operations = ['Equals', 'Contains', 'Is in', '>', '<', '≥', '≤']
        self.loop_behaviors = ['Forever', 'Multiple times', 'For each element in list', 'For each row in table', 'For each column in table']

        def create_bitmaps(source_file_name: str, size: tuple, default_contrast=100, flip=False, hover_red=False):
            # manipulate default image
            image = wx.Image(f'data/{source_file_name}.png', wx.BITMAP_TYPE_PNG)  # import image
            image.Replace(*3 * (0,), *3 * (default_contrast,))  # change color from native black to lighter grey
            image = image.Scale(*size, quality=wx.IMAGE_QUALITY_HIGH)
            if flip:
                image = image.Mirror(horizontally=False)  # flip image about x-axis

            # manipulate hover image
            image_hover = wx.Image(f'data/{source_file_name}.png', wx.BITMAP_TYPE_PNG)  # import image
            if hover_red:
                image_hover.Replace(*3 * (0,), *(180, 0, 0))  # change color from native black to lighter grey
            image_hover = image_hover.Scale(*size, quality=wx.IMAGE_QUALITY_HIGH)
            if flip:
                image_hover = image_hover.Mirror(horizontally=False)  # flip image about x-axis

            return image.ConvertToBitmap(), image_hover.ConvertToBitmap()

        # create move up/down bitmaps
        self.move_btn_size = tuple([3 * dimen for dimen in [5, 3]])  # maintain 5:3 ratio
        self.up_arrow_bitmap, self.up_arrow_bitmap_hover = create_bitmaps('up_arrow', self.move_btn_size)
        self.down_arrow_bitmap, self.down_arrow_bitmap_hover = create_bitmaps('up_arrow', self.move_btn_size, flip=True)

        # create delete X bitmaps
        self.delete_x_size = 2 * (0.7 * self.move_btn_size[0],)
        self.delete_x_bitmap, self.delete_x_bitmap_hover = create_bitmaps('delete_x', self.delete_x_size, hover_red=True)

        # create back btn bitmaps
        self.back_btn_size = 2 * (1.2 * self.move_btn_size[0],)
        self.back_btn_bitmap, self.back_btn_bitmap_hover = create_bitmaps('back_arrow', self.back_btn_size)

        # create sizers
        self.vbox_container = wx.BoxSizer(wx.VERTICAL)
        fg_sizer = wx.FlexGridSizer(2, 2, 10, 10)

        self.hbox_top = wx.BoxSizer(wx.HORIZONTAL)  # ------------------------------------------------------------------

        # add back button
        self.back_btn = self.create_bitmap_btn(self, self.back_btn_size, self.back_btn_bitmap, 'back_btn',
                                               'Back to workflow selection', focus_change=False)
        self.back_btn.Bind(wx.EVT_BUTTON, lambda event: self.close_window())
        self.back_btn.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)

        self.hbox_top.Add(self.back_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        # self.hbox_top.AddSpacer(10)

        # add workflow title
        self.title = wx.Button(self, label=self.workflow_name, style=wx.BORDER_NONE | wx.BU_EXACTFIT)
        self.title.SetBackgroundColour(wx.WHITE)
        self.title.Bind(wx.EVT_BUTTON, self.rename_workflow)
        change_font(self.title, size=18, color=3 * (60,))
        self.hbox_top.Add(self.title, 0, wx.ALIGN_CENTER_VERTICAL)

        self.vbox_action = wx.BoxSizer(wx.VERTICAL)  # sizer for action sidebar
        self.hbox_line_mods = wx.BoxSizer(wx.HORIZONTAL)

        # add delete command button
        self.delete_btn = wx.Button(self, label='-', size=(20, -1))
        self.delete_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_delete_command_dialog())
        config_status_and_tooltip(self, self.delete_btn, 'Delete commands', 'Delete commands')
        self.hbox_line_mods.Add(self.delete_btn, 1)
        self.hbox_line_mods.AddSpacer(2)

        # add plus command button
        self.plus_btn = wx.Button(self, label='+', size=(20, -1))
        self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_add_command_dialog())
        config_status_and_tooltip(self, self.plus_btn, 'Add commands', 'Add commands')
        self.hbox_line_mods.Add(self.plus_btn, 1)

        self.vbox_action.Add(self.hbox_line_mods, 0, wx.EXPAND | wx.SOUTH, 5)

        # add reorder commands button
        self.reorder_btn = wx.Button(self, label='Reorder')
        self.reorder_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_reorder_dialog())
        config_status_and_tooltip(self, self.reorder_btn, 'Reorder commands', 'Reorder commands')
        self.vbox_action.Add(self.reorder_btn, 0, wx.EXPAND | wx.SOUTH, 10)

        # add advanced command button
        self.advanced_btn = wx.Button(self, label='Advanced')
        self.advanced_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_advanced_edit_frame())
        config_status_and_tooltip(self, self.advanced_btn, 'Advanced text-based editor', 'Advanced text-based editor')
        self.vbox_action.Add(self.advanced_btn, 0, wx.EXPAND)

        self.vbox_action.AddStretchSpacer()

        # add record command button
        self.record_btn = wx.Button(self, label='Record')
        self.record_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_record())
        config_status_and_tooltip(self, self.record_btn, 'Record workflow actions', 'Record workflow actions')
        self.vbox_action.Add(self.record_btn, 0, wx.EXPAND | wx.SOUTH, 10)

        # add execute command button
        self.execute_btn = wx.Button(self, label='Execute')
        self.execute_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_execute())
        self.execute_btn.SetFocus()
        config_status_and_tooltip(self, self.execute_btn, 'Execute workflow actions', 'Execute workflow actions')
        self.vbox_action.Add(self.execute_btn, 0, wx.EXPAND)

        self.vbox_edit_container = wx.BoxSizer(wx.VERTICAL)
        self.vbox_edit_container.AddStretchSpacer()

        fg_sizer.AddMany(
            [(self.hbox_top, 1, wx.EXPAND), (wx.BoxSizer(wx.HORIZONTAL)), (self.vbox_edit_container, 1, wx.EXPAND),
             (self.vbox_action, 1, wx.EXPAND)])
        fg_sizer.AddGrowableCol(0, 0)
        fg_sizer.AddGrowableRow(1, 0)
        # --------------------------------------------------------------------------------------------------------------

        # add margins and inside sizers
        self.vbox_container.Add(fg_sizer, 1, wx.EXPAND | wx.ALL, self.margin)
        self.create_edit_panel(first_creation=True)
        self.vbox_container.SetSizeHints(self)
        self.SetSizer(self.vbox_container)
        self.Center()
        self.Bind(wx.EVT_CLOSE, lambda event: self.close_window(quitall=True))
        self.Show()

        # add command widgets
        self.edit.Freeze()
        self.render_lines()
        self.edit.Thaw()

        # all tracker lists must be modified when altering command order or adding/deleting
        self.tracker_lists = [self.lines, self.edit_row_container_sizers, self.edit_row_widget_sizers, self.indents]

        print(f'Time to open entire Edit frame ({len(self.lines)}): {time.time() - t0:.2f} s')

    def create_bitmap_btn(self, parent, size, bitmap, hover_keyword, description, tooltip='', focus_change=True):
        bitmap_btn = wx.BitmapButton(parent, size=wx.Size(*size), bitmap=bitmap)
        bitmap_btn.SetBackgroundColour(wx.WHITE)
        bitmap_btn.SetWindowStyleFlag(wx.NO_BORDER)
        bitmap_btn.Bind(wx.EVT_ENTER_WINDOW, lambda event: self.button_hover_on(event, hover_keyword))
        bitmap_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda event: self.button_hover_off(event, hover_keyword))
        if focus_change:
            bitmap_btn.Bind(wx.EVT_SET_FOCUS, lambda event: self.button_hover_on(event, hover_keyword))
            bitmap_btn.Bind(wx.EVT_KILL_FOCUS, lambda event: self.button_hover_off(event, hover_keyword))
        config_status_and_tooltip(self, bitmap_btn, description, tooltip)
        return bitmap_btn

    def rename_workflow(self, _):

        self.char_limit = 35

        # create rename text entry text dialog
        rename_dlg = wx.TextEntryDialog(self, f'Enter Your New Name for "{self.workflow_name}"', 'Rename Workflow')
        rename_dlg.SetMaxLength(self.char_limit)
        text_ctrl = rename_dlg.FindWindowById(3000)
        text_ctrl.Validator = self.CharValidator('file_name', self)  # assign validator for filename

        if rename_dlg.ShowModal() == wx.ID_OK:
            if rename_dlg.GetValue().strip():  # if the entry is not empty or only spaces
                self.workflow_name = rename_dlg.GetValue().capitalize()
                self.title.SetForegroundColour(wx.WHITE)  # hide button manipulation
                self.title.SetLabel(self.workflow_name)
                self.title.SetForegroundColour(wx.BLACK)
                self.Layout()
                self.SetTitle(f'{self.software_info.name}: Edit - {self.workflow_name}')
        rename_dlg.Destroy()

    def create_edit_panel(self, first_creation=False):
        self.edit_row_container_sizers = []  # for looping and manipulating sizers with staticlines
        self.edit_row_widget_sizers = []  # for identifying indices later

        # if self.vbox_edit:
        if not first_creation:  # if edit panel has been created previously
            self.edit.Destroy()

        self.edit = wx.lib.scrolledpanel.ScrolledPanel(self, style=wx.SIMPLE_BORDER)
        self.edit.SetupScrolling()

        self.vbox_edit = wx.BoxSizer(wx.VERTICAL)
        self.edit.SetSizer(self.vbox_edit)

        self.vbox_edit_container_temp = wx.BoxSizer(wx.VERTICAL)  # temp inserted so can replace later
        self.vbox_container.Replace(self.vbox_edit_container, self.vbox_edit_container_temp, recursive=True)

        self.vbox_edit_container = wx.BoxSizer(wx.VERTICAL)
        self.vbox_edit_container.Add(self.edit, 1, wx.EXPAND)
        self.vbox_edit_container.SetMinSize(wx.Size(650, 300))
        self.vbox_container.Replace(self.vbox_edit_container_temp, self.vbox_edit_container, recursive=True)

        if not first_creation:
            self.render_lines()

    def render_lines(self):
        # delete all leading and trailing empty lines
        try:
            for index in [0, -1]:
                while self.lines[index] == '':
                    del self.lines[index]
        except IndexError:
            pass

        # clear indent pattern
        self.indents = [0]
        self.next_indent = 0

        if len(self.lines) > self.loading_dlg_line_thresh:
            self.loading_dlg = wx.ProgressDialog(f'Aldras Loading "{self.workflow_name}"',
                                                 'Loading...',
                                                 maximum=len(self.lines), parent=self,
                                                 style=wx.PD_AUTO_HIDE | wx.PD_APP_MODAL | wx.PD_SMOOTH | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
            self.loading_dlg.SetIcon(
                wx.Icon(self.software_info.icon, wx.BITMAP_TYPE_ICO))  # doesn't seem to have effect

        for index, line_orig in enumerate(self.lines):
            self.create_command_sizer(index, line_orig)
            if len(self.lines) > self.loading_dlg_line_thresh:
                # update loading dialog and return to SelectionFrame if cancelled
                if not self.loading_dlg.Update(0.99 * (index + 1), f'Loading line {index + 1} of {len(self.lines)}.')[0]:
                    self.loading_dlg.Show(False)
                    self.loading_dlg.Destroy()
                    self.close_window()
                    return

        if len(self.lines) > self.loading_dlg_line_thresh:
            self.loading_dlg.Destroy()

        for self.edit_row in self.edit_row_container_sizers:
            self.command_row_error = False
            command_widgets = self.edit_row.GetChildren()[0].GetSizer().GetChildren()
            try:
                combobox_window = command_widgets[1].GetWindow()
                if combobox_window:
                    text_ctrls = [widget.GetWindow() for widget in command_widgets if (
                            isinstance(widget.GetWindow(), wx.TextCtrl) and not isinstance(widget.GetWindow(),
                                                                                           wx.lib.expando.ExpandoTextCtrl))]
                    for text_ctrl in text_ctrls:
                        if not self.command_row_error:
                            text_ctrl.SetValue(text_ctrl.GetValue())  # trigger wx.EVT_TEXT events to validate entry
            except IndexError:
                pass
        self.Layout()

    def create_command_sizer(self, index, line_orig):
        self.line = line_orig.lower()
        self.hbox_edit = wx.BoxSizer(wx.HORIZONTAL)
        self.no_right_spacer = False
        end_indent = False

        # add spacer for commands are within conditional
        indent_static_text = wx.StaticText(self.edit, label='', name='indent_text')
        change_font(indent_static_text, size=1)
        self.hbox_edit.Add(indent_static_text, 0, wx.ALIGN_CENTER_VERTICAL)

        try:
            if self.line.strip() == '}':  # do not add row for ending indent bracket
                self.next_indent -= 1
                if self.next_indent < 0:
                    self.next_indent = 0
                    raise ValueError
                end_indent = True
            else:
                # add move buttons
                self.vbox_move = wx.BoxSizer(wx.VERTICAL)  # ---------------------------------------------------------------

                self.move_up = self.create_bitmap_btn(self.edit, self.move_btn_size, self.up_arrow_bitmap, 'move_up',
                                                      'Move command up')
                self.move_up.Bind(wx.EVT_BUTTON, lambda event, sizer_trap=self.hbox_edit: self.move_command_up(sizer_trap))
                self.vbox_move.Add(self.move_up, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, 5)
                if index == 0:
                    self.move_up.Show(False)  # hide move up button if topmost command

                # add spacer to preserve width (mainly for when adding single command)
                self.vbox_move.Add(self.vbox_move.GetSize()[0], -1, 0)

                self.move_down = self.create_bitmap_btn(self.edit, self.move_btn_size, self.down_arrow_bitmap, 'move_down',
                                                        'Move command down')
                self.move_down.Bind(wx.EVT_BUTTON,
                                    lambda event, sizer_trap=self.hbox_edit: self.move_command_down(sizer_trap))
                self.vbox_move.Add(self.move_down, 0, wx.ALIGN_CENTER_HORIZONTAL)
                if index == len(self.lines) - 1:
                    self.move_down.Show(False)  # hide move down button if bottommost command

                self.hbox_edit.Add(self.vbox_move, 0, wx.ALIGN_CENTER_VERTICAL | wx.WEST | wx.EAST, 8)
                # ----------------------------------------------------------------------------------------------------------

                self.line_first_word = self.line.strip().split(' ')[0]

                if not self.line:  # if line is empty, insert spacers
                    self.hbox_edit.Insert(0, 0, 50, 1)
                    self.hbox_edit.Insert(0, 0, 0, 1)

                elif '#' in self.line_first_word:  # workflow comment
                    self.add_command_combobox('Comment')
                    self.create_comment_row(line_orig)

                elif '-mouse' in self.line_first_word:
                    self.add_command_combobox('Mouse button')
                    self.create_mouse_row(self.line)

                elif 'type:' in self.line_first_word:
                    self.add_command_combobox('Type')
                    self.create_type_row(line_orig)

                elif 'wait' in self.line_first_word:
                    self.add_command_combobox('Wait')
                    self.create_wait_row(self.line)

                elif 'hotkey' in self.line_first_word:
                    self.add_command_combobox('Hotkey')
                    self.create_hotkey_row(self.line)

                elif 'key' in self.line_first_word:
                    self.key_in = self.line.split(' ')[1]

                    if self.key_in in [x.lower() for x in self.software_info.special_keys]:
                        key_type = 'Special key'
                    elif self.key_in in [x.lower() for x in self.software_info.function_keys]:
                        key_type = 'Function key'
                    elif self.key_in in [x.lower() for x in self.software_info.media_keys]:
                        key_type = 'Media key'
                    else:
                        raise ValueError

                    self.add_command_combobox(key_type)
                    self.create_key_row(self.line)

                elif ('mouse' in self.line_first_word) and ('move' in self.line_first_word):
                    self.add_command_combobox('Mouse-move')
                    self.create_mousemove_row(self.line)

                elif ('double' in self.line) and ('click' in self.line):
                    self.add_command_combobox('Double-click')
                    self.create_multi_click_row(self.line)

                elif ('triple' in self.line) and ('click' in self.line):
                    self.add_command_combobox('Triple-click')
                    self.create_multi_click_row(self.line)

                elif ('assign' in self.line_first_word) and ('{{~' in self.line) and ('~}}' in self.line):
                    self.add_command_combobox('Assign')
                    self.create_assign_var_row(line_orig)

                elif ('if' in self.line_first_word) and ('{' in self.line):
                    self.add_command_combobox('Conditional')
                    self.create_conditional_row(line_orig)

                elif ('loop' in self.line_first_word) and ('{' in self.line):
                    self.add_command_combobox('Loop')
                    self.create_loop_row(line_orig)

                else:
                    raise ValueError

        except ValueError:
            # display indecipherable line
            self.add_command_combobox('')
            self.hbox_edit.AddSpacer(10)
            self.unknown_cmd_msg = non_flickering_static_text(self.edit, f'**Unknown command from line: "{self.line}"')
            change_font(self.unknown_cmd_msg, size=9, style=wx.ITALIC, color=3 * (70,))
            self.hbox_edit.Add(self.unknown_cmd_msg, 0, wx.ALIGN_CENTER_VERTICAL)

        if not end_indent:
            self.create_delete_x_btn(self.hbox_edit)

        indent_static_text.SetLabel(self.indents[-1] * 20 * ' ')
        self.indents.insert(index+1, self.next_indent)

        self.edit_row_widget_sizers.insert(index, self.hbox_edit)

        # add bottom static line below command
        edit_row_vbox = wx.BoxSizer(wx.VERTICAL)
        vertical_padding = 5 if not end_indent else 0
        edit_row_vbox.Add(self.hbox_edit, 0, wx.EXPAND | wx.NORTH | wx.SOUTH, vertical_padding)
        if not end_indent:
            edit_row_vbox.Add(wx.StaticLine(self.edit), 0, wx.EXPAND)

        self.edit_row_container_sizers.insert(index, edit_row_vbox)
        self.vbox_edit.Insert(index, edit_row_vbox, 0, wx.EXPAND)

    def create_delete_x_btn(self, sizer):
        sizer.AddSpacer(15)
        if not self.no_right_spacer:
            sizer.AddStretchSpacer()

        delete_x_button = self.create_bitmap_btn(self.edit, self.delete_x_size, self.delete_x_bitmap, 'delete_x',
                                                 'Delete command')
        delete_x_button.Bind(wx.EVT_BUTTON, lambda _: self.delete_command(sizer))
        sizer.Add(delete_x_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

    def button_hover_on(self, event, btn_kind):
        btn = event.GetEventObject()
        # replace button bitmap with faded version
        if btn_kind == 'move_up':
            btn.SetBitmap(self.up_arrow_bitmap_hover)
        elif btn_kind == 'move_down':
            btn.SetBitmap(self.down_arrow_bitmap_hover)
        elif btn_kind == 'delete_x':
            btn.SetBitmap(self.delete_x_bitmap_hover)
        elif btn_kind == 'back_btn':
            btn.SetBitmap(self.back_btn_bitmap_hover)

    def button_hover_off(self, event, btn_kind):
        btn = event.GetEventObject()
        # replace button bitmap with non-faded version
        if btn_kind == 'move_up':
            btn.SetBitmap(self.up_arrow_bitmap)
        elif btn_kind == 'move_down':
            btn.SetBitmap(self.down_arrow_bitmap)
        elif btn_kind == 'delete_x':
            btn.SetBitmap(self.delete_x_bitmap)
        elif btn_kind == 'back_btn':
            btn.SetBitmap(self.back_btn_bitmap)

    def add_command_combobox(self, command_value):
        self.command = wx.ComboBox(self.edit, value=command_value, choices=self.software_info.commands,
                                   style=wx.CB_READONLY, name='command')
        self.command.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
        self.command.Bind(wx.EVT_COMBOBOX,
                          lambda event, sizer_trap=self.hbox_edit: self.command_combobox_change(sizer_trap, event))
        self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)
        self.hbox_edit.AddSpacer(10)

    class CharValidator(wx.Validator):
        """ Validates data as it is entered into the text controls. """

        def __init__(self, flag, parent):
            wx.Validator.__init__(self)
            self.flag = flag
            self.parent = parent
            self.Bind(wx.EVT_CHAR, self.on_char)

        def Clone(self):
            """Required Validator method"""
            return self.parent.CharValidator(self.flag, self.parent)

        def TransferToWindow(self):
            return True

        def TransferFromWindow(self):
            return True

        def Validate(self, win):  # used when transferred to window
            if self.flag == 'file_name':
                valid = True
                text_ctrl = self.Window
                value = text_ctrl.Value.capitalize()
                proposed_file_name = f'{self.parent.parent.workflow_directory}/{value}.txt'

                if not value.strip():  # if empty string or only spaces
                    valid = False
                    wx.MessageDialog(None, f'Enter a file name or cancel',
                                     'Invalid file name', wx.OK | wx.ICON_WARNING).ShowModal()

                try:
                    if os.path.exists(proposed_file_name):
                        valid = False
                        wx.MessageDialog(None, f'Enter a file name for a file that does not already exist',
                                         'Taken file name', wx.OK | wx.ICON_WARNING).ShowModal()
                    else:
                        with open(proposed_file_name, 'w') as _:  # try to create file to validate file name
                            pass
                        os.remove(proposed_file_name)
                except OSError:
                    valid = False
                    wx.MessageDialog(None, f'Enter a valid file name for your operating system',
                                     'Invalid file name', wx.OK | wx.ICON_WARNING).ShowModal()
                return valid
            else:
                raise ValueError('Validator flag not defined')

        def on_char(self, event):
            # process character
            keycode = int(event.GetKeyCode())
            if keycode < 256 and not keycode in [8, 127]:  # don't ignore backspace(8) or delete(127)
                key = chr(keycode)
                # return and do not process key if conditions are met
                if self.flag == 'no_alpha' and key in string.ascii_letters:
                    return
                if self.flag == 'only_digit' and not (key.isdecimal() or key == '.'):
                    return
                if self.flag == 'only_integer' and not key.isdecimal():
                    return
                if self.flag == 'file_name':
                    invalid_file_characters = ['<', '>', ':', '\"', '\\', '/', '|', '?', '*']
                    if key in invalid_file_characters:
                        return
                if self.flag == 'variable_name':
                    invalid_variable_characters = ['<', '>', ':', '\"', '\\', '/', '|', '?', '*', '.']
                    if key in invalid_variable_characters:
                        return

            event.Skip()
            return

    def create_mouse_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        if 'left' in line:
            button = 'Left'
        elif 'right' in line:
            button = 'Right'
        else:
            raise ValueError
        mouse_button = wx.ComboBox(self.edit, value=button, choices=self.software_info.mouse_buttons,
                                   style=wx.CB_READONLY)
        mouse_button.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
        mouse_button.Bind(wx.EVT_COMBOBOX, lambda event: self.mouse_command_change(sizer, event))

        if 'click' in line:
            action = 'Click'
        elif 'press' in line:
            action = 'Press'
        elif 'release' in line:
            action = 'Release'
        else:
            mouse_button.Show(False)
            raise ValueError
        mouse_action = wx.ComboBox(self.edit, value=action, choices=self.software_info.mouse_actions,
                                   style=wx.CB_READONLY)
        mouse_action.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
        mouse_action.Bind(wx.EVT_COMBOBOX, lambda event: self.mouse_command_change(sizer, event))

        sizer.Add(mouse_button, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(mouse_action, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(non_flickering_static_text(self.edit, 'at pt. (  '), 0, wx.ALIGN_CENTER_VERTICAL)

        self.create_point_input(line, sizer)

    def create_point_input(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        x_val = coords_of(line)[0]
        y_val = coords_of(line)[1]

        self.x_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE | wx.TE_RICH,
                                   size=wx.Size(self.software_info.coord_width, -1),
                                   value=str(x_val),
                                   validator=self.CharValidator('only_integer', self))
        self.x_coord.SetMaxLength(len(str(display_size[0])))
        self.x_coord.Bind(wx.EVT_TEXT, lambda event: self.coord_change(sizer, event, x=True))
        self.x_coord.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)

        self.y_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE | wx.TE_RICH,
                                   size=wx.Size(self.software_info.coord_width, -1),
                                   value=str(y_val),
                                   validator=self.CharValidator('only_integer', self))
        self.y_coord.SetMaxLength(len(str(display_size[1])))
        self.y_coord.Bind(wx.EVT_TEXT, lambda event: self.coord_change(sizer, event, y=True))
        self.y_coord.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)

        sizer.Add(self.x_coord, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(non_flickering_static_text(self.edit, ' , '), 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.y_coord, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(non_flickering_static_text(self.edit, '  )'), 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(25)
        self.error_display = non_flickering_static_text(self.edit, '')
        self.error_display.SetName('error_display')
        self.error_display.SetForegroundColour(wx.RED)
        sizer.Add(self.error_display, 0, wx.ALIGN_CENTER_VERTICAL)

    def create_type_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        text_value = str(line).replace('type:', '').replace('Type:', '')
        text_to_type = wx.lib.expando.ExpandoTextCtrl(self.edit, value=text_value)
        text_to_type.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'type'))
        sizer.Add(text_to_type, 1, wx.EXPAND)
        self.no_right_spacer = True

    def create_wait_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        value = '0'
        if not sizer:
            sizer = self.hbox_edit
            value = line.replace('wait', '').replace(' ', '')

        wait_entry = wx.TextCtrl(self.edit, value=value, style=wx.TE_RICH,
                                 validator=self.CharValidator('only_digit', self))
        wait_entry.Bind(wx.EVT_TEXT, lambda event: self.wait_change(sizer, event))
        wait_entry.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        sizer.Add(wait_entry, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(30)
        self.error_display = non_flickering_static_text(self.edit, '')
        self.error_display.SetName('error_display')
        sizer.Add(self.error_display, 0, wx.ALIGN_CENTER_VERTICAL)

    def create_key_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        key_in = line.split(' ')[1]

        if key_in in [x.lower() for x in self.software_info.special_keys]:
            choices = self.software_info.special_keys
        elif key_in in [x.lower() for x in self.software_info.function_keys]:
            choices = self.software_info.function_keys
        elif key_in in [x.lower() for x in self.software_info.media_keys]:
            choices = self.software_info.media_keys
        else:
            raise ValueError('Key category not specified.')

        key = wx.ComboBox(self.edit, value=str(key_in), choices=choices, style=wx.CB_READONLY)
        key.Bind(wx.EVT_COMBOBOX, lambda event: self.key_change(sizer, event))
        key.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel

        if 'tap' in line:
            action = 'Tap'
        elif 'press' in line:
            action = 'Press'
        elif 'release' in line:
            action = 'Release'
        else:
            raise ValueError
        key_action = wx.ComboBox(self.edit, value=action, choices=self.software_info.key_actions, style=wx.CB_READONLY)
        key_action.Bind(wx.EVT_COMBOBOX, lambda event: self.key_action_change(sizer, event))
        key_action.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel

        sizer.Add(key, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(key_action, 0, wx.ALIGN_CENTER_VERTICAL)

    def create_hotkey_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        combination = [x.capitalize() for x in
                       line.replace('hotkey', '').replace(' ', '').split('+')]  # create list of keys
        combination += [''] * (
                self.num_hotkeys - len(combination))  # extend list with empty strings to reach standard number

        for index, key in enumerate(combination):
            hotkey_cb = wx.ComboBox(self.edit, value=str(key), choices=self.software_info.all_keys,
                                    style=wx.CB_READONLY)
            hotkey_cb.Bind(wx.EVT_COMBOBOX, lambda event: self.hotkey_change(sizer, event))
            hotkey_cb.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
            sizer.Add(hotkey_cb, 0, wx.ALIGN_CENTER_VERTICAL)

            if index < len(combination) - 1:
                # only add '+' in between keys (not after)
                sizer.Add(non_flickering_static_text(self.edit, '  +  '), 0, wx.ALIGN_CENTER_VERTICAL)

    def create_mousemove_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        sizer.Add(non_flickering_static_text(self.edit, 'to pt. (  '), 0, wx.ALIGN_CENTER_VERTICAL)

        self.create_point_input(line, sizer)

    def create_multi_click_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        sizer.Add(non_flickering_static_text(self.edit, 'at pt. (  '), 0, wx.ALIGN_CENTER_VERTICAL)

        self.create_point_input(line, sizer)

    def create_comment_row(self, line_orig, sizer=None):
        if not sizer:
            sizer = self.hbox_edit

        sizer.AddStretchSpacer()

        comment_label = non_flickering_static_text(self.edit, '#')
        comment_contrast = 100
        change_font(comment_label, size=12, color=3 * (comment_contrast,))
        sizer.Add(comment_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.WEST | wx.EAST, 5)

        comment_value = str(line_orig).replace('#', '').strip()
        comment = wx.lib.expando.ExpandoTextCtrl(self.edit, value=comment_value, style=wx.TE_RIGHT)
        change_font(comment, size=10, style=wx.ITALIC, color=3 * (comment_contrast,))
        comment.Bind(wx.lib.expando.EVT_ETC_LAYOUT_NEEDED,
                     lambda _: self.Layout())  # layout EditFrame when ExpandoTextCtrl size changes
        comment.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'comment'))
        sizer.Add(comment, 2, wx.EXPAND)
        self.no_right_spacer = True

    def create_assign_var_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        variable_name_entry = wx.TextCtrl(self.edit, value=variable_name_in(line), style=wx.TE_RICH | wx.TE_RIGHT, validator=self.CharValidator('variable_name', self))
        change_font(variable_name_entry, weight=wx.BOLD)
        variable_name_entry.SetMaxLength(15)
        variable_name_entry.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'assign_var_name'))
        variable_name_entry.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        sizer.Add(variable_name_entry, 0, wx.ALIGN_CENTER_VERTICAL)

        equals_text = non_flickering_static_text(self.edit, '  =  ')
        change_font(equals_text, size=14)
        sizer.Add(equals_text, 0, wx.ALIGN_CENTER_VERTICAL)

        variable_value_entry = wx.lib.expando.ExpandoTextCtrl(self.edit, value=assignment_variable_value_in(line))
        variable_value_entry.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'assign_var_value'))
        variable_value_entry.Bind(wx.lib.expando.EVT_ETC_LAYOUT_NEEDED, lambda _: self.Layout())  # layout EditFrame when ExpandoTextCtrl size changes
        sizer.Add(variable_value_entry, 1, wx.ALIGN_CENTER_VERTICAL)
        self.no_right_spacer = True

    def create_conditional_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        if_text = non_flickering_static_text(self.edit, 'If')
        change_font(if_text, size=11)
        sizer.Add(if_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 8)

        variable_name_entry = wx.TextCtrl(self.edit, value=variable_name_in(line), style=wx.TE_RICH | wx.TE_RIGHT,
                                          validator=self.CharValidator('variable_name', self))
        change_font(variable_name_entry, weight=wx.BOLD)
        variable_name_entry.SetMaxLength(15)
        variable_name_entry.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'conditional_var_name'))
        variable_name_entry.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        sizer.Add(variable_name_entry, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 5)

        operation = wx.ComboBox(self.edit, value=conditional_operation_in(line, self.conditional_operations), choices=self.conditional_operations, style=wx.CB_READONLY)
        operation.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'conditional_comparison_operator'))

        operation.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
        sizer.Add(operation, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 5)

        comparison_entry = wx.lib.expando.ExpandoTextCtrl(self.edit, value=conditional_comparison_in(line))
        comparison_entry.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'conditional_comparison_value'))
        comparison_entry.Bind(wx.lib.expando.EVT_ETC_LAYOUT_NEEDED,
                                  lambda _: self.Layout())  # layout EditFrame when ExpandoTextCtrl size changes
        sizer.Add(comparison_entry, 1, wx.ALIGN_CENTER_VERTICAL)
        self.no_right_spacer = True
        self.next_indent += 1

    def create_loop_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        try:
            behavior_value = [element for element in self.loop_behaviors if element.lower() in line.lower()][0]
        except IndexError:
            raise ValueError

        behavior_cb = wx.ComboBox(self.edit, value=behavior_value, choices=self.loop_behaviors, style=wx.CB_READONLY)
        # behavior_cb.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'DESCRIPTOR'))
        behavior_cb.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
        sizer.Add(behavior_cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        if behavior_value == 'Forever':
            return
        elif behavior_value == 'Multiple times':
            loop_iteration_number = wx.TextCtrl(self.edit, value=re.search(r'\d+', line).group(), size=wx.Size(self.software_info.coord_width, -1), style=wx.TE_RICH | wx.TE_CENTRE, validator=self.CharValidator('only_integer', self))
            loop_iteration_number.SetMaxLength(4)
            # loop_iteration_number.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'DESCRIPTOR'))
            loop_iteration_number.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
            sizer.Add(loop_iteration_number, 0, wx.ALIGN_CENTER_VERTICAL)
        elif behavior_value == 'For each element in list':
            list_btn = wx.Button(self.edit, label='List')
            list_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_loop_list_grid(line))
            sizer.Add(list_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        # comparison_entry = wx.lib.expando.ExpandoTextCtrl(self.edit, value=conditional_comparison_in(line))
        # comparison_entry.Bind(wx.EVT_TEXT, lambda event: self.text_change(sizer, event, 'conditional_comparison_value'))
        # comparison_entry.Bind(wx.lib.expando.EVT_ETC_LAYOUT_NEEDED,
        #                           lambda _: self.Layout())  # layout EditFrame when ExpandoTextCtrl size changes
        # sizer.Add(comparison_entry, 1, wx.ALIGN_CENTER_VERTICAL)

        self.next_indent += 1

    def open_delete_command_dialog(self):

        class DeleteCommandsDialog(wx.Dialog):
            """Dialog to delete commands."""

            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
                self.SetIcon(wx.Icon(parent.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.SetTitle(f'Delete Commands - {parent.workflow_name}')
                self.SetBackgroundColour('white')

                sizer = wx.BoxSizer(wx.VERTICAL)

                sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Please choose the commands to delete:'), 0,
                          wx.ALL | wx.EXPAND, 5)

                # add list of checkboxes
                choices = [] if parent.lines is None else parent.lines
                self.check_list_box = wx.CheckListBox(self, wx.ID_ANY, choices=choices, size=(300, -1),
                                                      style=wx.LB_HSCROLL)
                sizer.Add(self.check_list_box, 1, wx.ALL | wx.EXPAND, 5)

                # select all checkbox
                self.checkbox = wx.CheckBox(self, wx.ID_ANY, 'Select all')
                self.checkbox.Bind(wx.EVT_CHECKBOX, self.check_all)
                sizer.Add(self.checkbox, 0, wx.ALL | wx.EXPAND, 5)

                self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
                sizer.Add(self.btns, 0, wx.ALL | wx.EXPAND, 5)

                self.SetSizerAndFit(sizer)
                self.Center()

            def get_selections(self):
                return self.check_list_box.GetCheckedItems()

            def check_all(self, _):
                # select all commands
                state = self.checkbox.IsChecked()
                for item_index in range(self.check_list_box.GetCount()):
                    self.check_list_box.Check(item_index, state)

        delete_dlg = DeleteCommandsDialog(self)

        if delete_dlg.ShowModal() == wx.ID_OK:
            indices_to_delete = delete_dlg.get_selections()
            if indices_to_delete:  # if indices_to_delete is not empty
                for index in sorted(indices_to_delete, reverse=True):
                    del (self.lines[index])
                    del (self.edit_row_container_sizers[index])
                    del (self.edit_row_widget_sizers[index])
                    self.vbox_edit.Show(index, False)
                    self.vbox_edit.Remove(index)
                self.vbox_edit.Layout()
                self.Layout()

    def open_add_command_dialog(self):
        self.default_new_command = f'Left-mouse click at {self.default_coords}'
        self.lines.append(self.default_new_command)
        new_line_index = len(self.lines) - 1

        self.create_command_sizer(new_line_index, self.lines[-1])

        # show move-down button of previously bottom-most command
        try:
            self.show_move_button(self.edit_row_container_sizers[-2], 'down', True)
        except IndexError:
            pass

        self.vbox_edit.Layout()
        self.Layout()

        self.edit.ScrollChildIntoView([child.GetWindow() for child in list(self.hbox_edit.GetChildren()) if
                                       isinstance(child.GetWindow(), wx.ComboBox)][-1])
        self.Layout()

    def open_reorder_dialog(self):
        reorder_character_cutoff = 50
        items = [f'{line[:reorder_character_cutoff]}...' if len(line) > reorder_character_cutoff else line for line in
                 self.lines]
        order = range(len(self.lines))

        # TODO replace with wx.RearrangeCtrl or wx.RearrangeList
        reorder_dlg = wx.RearrangeDialog(None, 'The checkboxes do not matter',
                                         f'Reorder Commands - {self.workflow_name}', order, items)
        reorder_dlg.SetIcon(wx.Icon(self.software_info.icon, wx.BITMAP_TYPE_ICO))

        # center dialog
        reorder_dlg.Position = (self.Position[0] + ((self.Size[0] - reorder_dlg.Size[0]) / 2),
                                self.Position[1] + ((self.Size[1] - reorder_dlg.Size[1]) / 2))
        reorder_dlg.SetBackgroundColour('white')

        if reorder_dlg.ShowModal() == wx.ID_OK:
            order = reorder_dlg.GetOrder()
            print(f'reordered indices: {order}')
            if order != list(range(len(order))):  # only perform operations if order changes
                self.lines = [self.lines[index] for index in order]
                self.create_edit_panel()

    def open_advanced_edit_frame(self):

        class AdvancedEdit(wx.Dialog):
            def __init__(self, parent):
                wx.Dialog.__init__(self, parent,
                                   title=f'{parent.software_info.name}: Advanced Edit - {parent.workflow_name}',
                                   style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
                self.SetIcon(wx.Icon(parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.SetBackgroundColour('white')
                self.parent = parent
                self.adv_edit_guide = None

                # create sizers
                self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                self.vbox_inner = wx.BoxSizer(wx.VERTICAL)

                # add encompassing panel
                self.adv_edit_panel = wx.Panel(self)

                # add workflow title
                self.title = wx.StaticText(self.adv_edit_panel, label=parent.workflow_name)
                change_font(self.title, size=18, color=3 * (60,))
                self.vbox_inner.Add(self.title)

                self.vbox_inner.AddSpacer(5)

                self.text_edit = wx.TextCtrl(self.adv_edit_panel, value='\n'.join(parent.lines),
                                             style=wx.TE_MULTILINE | wx.EXPAND,
                                             size=(500, 250))

                self.vbox_inner.Add(self.text_edit, 1, wx.EXPAND)

                self.vbox_inner.AddSpacer(10)

                self.hbox_bottom_btns = wx.BoxSizer(wx.HORIZONTAL)  # --------------------------------------------------

                self.advanced_edit_guide_btn = wx.Button(self.adv_edit_panel, label='Guide')
                self.advanced_edit_guide_btn.Bind(wx.EVT_BUTTON, self.advanced_edit_guide)
                self.hbox_bottom_btns.Add(self.advanced_edit_guide_btn)

                self.hbox_bottom_btns.AddStretchSpacer()

                self.button_array = wx.StdDialogButtonSizer()
                self.ok_btn = wx.Button(self.adv_edit_panel, wx.ID_OK, label='OK')
                self.button_array.Add(self.ok_btn)
                self.button_array.AddSpacer(5)
                self.cancel_btn = wx.Button(self.adv_edit_panel, wx.ID_CANCEL, label='Cancel')
                self.button_array.Add(self.cancel_btn)
                self.hbox_bottom_btns.Add(self.button_array)

                self.vbox_inner.Add(self.hbox_bottom_btns, 0, wx.EXPAND)
                # ------------------------------------------------------------------------------------------------------

                self.vbox_outer.Add(self.vbox_inner, 1, wx.EXPAND | wx.ALL, 10)

                self.adv_edit_panel.SetSizer(self.vbox_outer)
                self.vbox_outer.SetSizeHints(self)
                self.Center()
                self.Bind(wx.EVT_CLOSE, self.close_window)

            def advanced_edit_guide(self, _):

                class AdvancedEditGuide(wx.Dialog):
                    def __init__(self, parent):
                        self.software_info = parent.parent.software_info
                        self.workflow_name = parent.parent.workflow_name
                        wx.Dialog.__init__(self, parent.parent, title=f'{self.software_info.name} Edit Guide',
                                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
                        self.SetBackgroundColour('white')

                        # create sizers
                        self.hbox_outer = wx.BoxSizer(wx.HORIZONTAL)
                        self.vbox_inner = wx.BoxSizer(wx.VERTICAL)
                        self.vbox_inner.AddStretchSpacer()

                        # add advanced edit guide title
                        self.title = wx.StaticText(self, label='Advanced Edit Guide')
                        self.title_contrast = 60
                        change_font(self.title, size=18, color=3 * (self.title_contrast,))
                        self.vbox_inner.Add(self.title)

                        self.vbox_inner.AddSpacer(5)

                        # add advanced edit guide description
                        self.hbox_description = wx.BoxSizer(wx.HORIZONTAL)
                        self.hbox_description.AddSpacer(5)
                        self.description = wx.StaticText(self, label=self.software_info.advanced_edit_guide_description)
                        self.description.SetToolTip('Feel free to use any capitalization scheme')
                        self.hbox_description.Add(self.description)
                        self.vbox_inner.Add(self.hbox_description)

                        self.vbox_inner.AddSpacer(20)

                        # add commands title
                        self.command_title = wx.StaticText(self, label='Commands')
                        change_font(self.command_title, size=14, color=3 * (self.title_contrast,))
                        self.command_title_contrast = self.title_contrast
                        self.vbox_inner.Add(self.command_title)

                        self.sbox_guide = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ''), wx.VERTICAL)
                        self.command_description = wx.StaticText(self,
                                                                 label=self.software_info.advanced_edit_guide_command_description)
                        change_font(self.command_description, size=10, family=wx.SWISS, style=wx.ITALIC)
                        self.sbox_guide.Add(self.command_description, 0, wx.ALIGN_RIGHT)

                        self.sbox_guide.AddSpacer(25)

                        # loop through commands
                        for command, data in self.software_info.advanced_edit_guide_commands.items():
                            example = data[0]
                            description = data[1]

                            # add command label
                            self.command = wx.StaticText(self, label=f'  {command}     ')
                            change_font(self.command, size=10, family=wx.SWISS, weight=wx.BOLD)
                            self.command.SetToolTip(description)
                            self.sbox_guide.Add(self.command)
                            self.sbox_guide.AddSpacer(5)

                            # add command example(s)
                            def formatted_example(example_text):
                                formatted_example_static_text = wx.StaticText(self, label=f'   {example_text}')
                                change_font(formatted_example_static_text, size=10, family=wx.MODERN, color=3 * (80,))
                                formatted_example_static_text.SetToolTip(description)
                                return formatted_example_static_text

                            if isinstance(example, list):
                                for each_example in example:
                                    self.sbox_guide.Add(formatted_example(each_example))
                            else:
                                self.sbox_guide.Add(formatted_example(example))

                            self.sbox_guide.AddSpacer(15)

                        self.vbox_inner.Add(self.sbox_guide)

                        self.vbox_inner.AddSpacer(20)

                        # add documentation title
                        self.docs = wx.StaticText(self, label='Read the Docs')
                        change_font(self.docs, size=13, family=wx.DECORATIVE, color=3 * (80,))
                        config_status_and_tooltip(self, self.docs, tooltip='More Documentation')
                        self.vbox_inner.Add(self.docs, 0, wx.CENTER)

                        # add documentation linke
                        self.docs_link = wx.adv.HyperlinkCtrl(self, wx.ID_ANY,
                                                              label=f'{self.software_info.name.lower()}.com/docs',
                                                              url=f'{self.software_info.website}/docs',
                                                              style=wx.adv.HL_DEFAULT_STYLE)
                        config_status_and_tooltip(self, self.docs_link, tooltip=f'{self.software_info.website}/docs')
                        change_font(self.docs_link, size=11, family=wx.DECORATIVE)
                        self.vbox_inner.Add(self.docs_link, 0, wx.CENTER)

                        self.vbox_inner.AddSpacer(25)
                        self.vbox_inner.AddStretchSpacer()

                        self.hbox_outer.AddStretchSpacer()
                        self.hbox_outer.Add(self.vbox_inner, 0, wx.CENTER | wx.EXPAND | wx.ALL, 10)
                        self.hbox_outer.AddStretchSpacer()

                        self.SetSizerAndFit(self.hbox_outer)
                        self.vbox_inner.SetSizeHints(self)

                        self.Show()

                if not self.adv_edit_guide or not self.adv_edit_guide.IsShown():  # only if window does not yet exist or is not shown
                    self.adv_edit_guide = AdvancedEditGuide(self)
                else:
                    self.adv_edit_guide.Raise()  # bring existing edit guide to top

            def close_window(self, close_event):
                if self.adv_edit_guide:
                    self.adv_edit_guide.Close(True)
                close_event.Skip()

        adv_edit_dlg = AdvancedEdit(self)
        if adv_edit_dlg.ShowModal() == wx.ID_OK:
            if adv_edit_dlg.text_edit.GetValue().split('\n') != self.lines:
                # TODO find way to only add changes rather than compute entire panel again
                self.lines = adv_edit_dlg.text_edit.GetValue().split('\n')
                self.create_edit_panel()
                self.Layout()

    def open_loop_list_grid(self, line):

        class LoopListGrid(wx.Dialog):
            """Dialog to edit loop list elements"""

            def __init__(self, parent, list_values):
                wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
                self.SetIcon(wx.Icon(parent.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.SetTitle(f'Loop List: - {parent.workflow_name}')
                self.SetBackgroundColour('white')

                spacing_between_fg_sizers = 10
                fg_sizer = wx.FlexGridSizer(1, 2, spacing_between_fg_sizers, spacing_between_fg_sizers)

                # create sizer for grid
                self.vbox_table = wx.BoxSizer(wx.VERTICAL)

                self.grid = CustomGrid(self, table_size=(40, 1), can_change_num_cols=False)
                self.grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
                self.grid.DisableColResize(0)

                # set grid cell values
                for index, loop_var_value in enumerate(list_values):
                    self.grid.SetCellValue(index, 0, loop_var_value)

                self.vbox_table.Add(self.grid, 1, wx.EXPAND)

                # add action widgets
                self.vbox_action = wx.BoxSizer(wx.VERTICAL)

                clear_btn = wx.Button(self, label='Clear Cell')
                clear_btn.Bind(wx.EVT_BUTTON, lambda event: self.grid.clear_cells())
                self.vbox_action.Add(clear_btn, 0, wx.EXPAND | wx.SOUTH, 10)

                clear_all_btn = wx.Button(self, label='Clear All')
                clear_all_btn.Bind(wx.EVT_BUTTON, lambda event: self.grid.clear_all_cells())
                self.vbox_action.Add(clear_all_btn, 0, wx.EXPAND | wx.SOUTH, 50)

                add_rows_btn = wx.Button(self, label='Add Rows')
                add_rows_btn.Bind(wx.EVT_BUTTON, lambda event: self.grid.AppendRows(10))
                self.vbox_action.Add(add_rows_btn, 0, wx.EXPAND)

                # TODO add link to spreadsheet

                self.vbox_action.AddStretchSpacer()

                ok_btn = wx.Button(self, wx.ID_OK, label='OK')
                self.vbox_action.Add(ok_btn, 0, wx.EXPAND | wx.SOUTH, 10)

                cancel_btn = wx.Button(self, wx.ID_CANCEL, label='Cancel')
                self.vbox_action.Add(cancel_btn, 0, wx.EXPAND)

                fg_sizer.AddMany([(self.vbox_table, 1, wx.EXPAND), (self.vbox_action, 1, wx.EXPAND)])
                fg_sizer.AddGrowableCol(0, 0)
                fg_sizer.AddGrowableRow(0, 0)

                margins = 10
                vbox_container = wx.BoxSizer(wx.HORIZONTAL)
                vbox_container.Add(fg_sizer, 1, wx.EXPAND | wx.ALL, margins)

                self.SetSizer(vbox_container)
                vbox_container.SetSizeHints(self)
                self.SetMinSize(wx.Size(vbox_container.GetSize()[0]+120, wx.GetDisplaySize()[1]/2))
                self.SetSize(self.GetMinSize())
                self.Center()
                self.Bind(wx.EVT_SIZE, self.resize_window)

                # set offset to autosize list column
                self.list_column_width_offset = self.vbox_action.GetMinSize()[0] + self.grid.GetRowLabelSize() + 2*margins + spacing_between_fg_sizers + 34

            def resize_window(self, event):
                """On window resize, resize column of list grid as well"""
                event.Skip()
                self.grid.SetColSize(0, self.GetSize()[0]-self.list_column_width_offset)
                self.grid.resize_rows()
                self.Refresh()

        loop_list_text = line[line.find('[') + 1:line.rfind(']')]  # find text between first '[' and last ']'
        loop_list_values = loop_list_text.split('```')  # split based on '```' delimiter

        loop_list_dlg = LoopListGrid(self, loop_list_values)

        if loop_list_dlg.ShowModal() == wx.ID_OK:
            pass

    def delete_command(self, sizer):
        index = self.edit_row_widget_sizers.index(sizer)

        for list_to_change in self.tracker_lists:
            del (list_to_change[index])

        self.vbox_edit.Show(index, False)
        self.vbox_edit.Remove(index)
        self.vbox_edit.Layout()
        self.Layout()

    def move_command_up(self, sizer):
        index = self.edit_row_widget_sizers.index(sizer)

        if index > 0:  # cannot move up top-most command
            row_sizer = self.edit_row_container_sizers[index].GetChildren()[0].GetSizer()
            command_value = matching_widget_in_edit_row(row_sizer, 'command').GetStringSelection()
            insertion_index = index  # location at which line that is 'in the way' will be inserted

            self.edit.Freeze()

            if command_value in ['Conditional', 'Loop']:  # move entire indented block

                # find index of last element of indented block
                next_same_indent_offset = self.indents[index+1:].index(self.indents[index])  # distance between indent start and end
                insertion_index = index + next_same_indent_offset  # index of end bracket, insertion occurs before this value

                if self.indents[index] > self.indents[index-1]:  # if moving out of surrounding indent block
                    for ii in range(index, insertion_index+1):
                        self.indents[ii] -= 1  # decrease indent of entire indent block
                elif self.indents[index] < self.indents[index-1]:  # if moving into surrounding indent block
                    for ii in range(index, insertion_index+1):
                        self.indents[ii] += 1  # increase indent of entire indent block
                for indent_index in range(index, insertion_index):
                    self.set_indent(indent_index)  # reset indents of indent block

            else:  # move single command row
                if self.indents[index] != self.indents[index-1]:
                    self.indents[index] = self.indents[index-1]  # set indent to preceding
                    self.set_indent(index)

            self.vbox_edit.Detach(index - 1)
            self.vbox_edit.Insert(insertion_index, self.edit_row_container_sizers[index - 1], 0, wx.EXPAND)

            for list_to_reorder in self.tracker_lists:
                list_to_reorder.insert(insertion_index, list_to_reorder.pop(index - 1))

            self.refresh_move_buttons()
            self.edit.Thaw()

    def move_command_down(self, sizer):
        index = self.edit_row_widget_sizers.index(sizer)

        if index < len(self.lines):  # cannot move up bottom-most command
            row_sizer = self.edit_row_container_sizers[index].GetChildren()[0].GetSizer()
            try:
                command_value = matching_widget_in_edit_row(row_sizer, 'command').GetStringSelection()
            except AttributeError:  # unknown command row (no command combobox)
                command_value = ''
            detachment_index = index  # location at which line that is 'in the way' will be detached

            self.edit.Freeze()

            if command_value in ['Conditional', 'Loop']:  # move entire indented block

                # find index of last element of indented block
                next_same_indent_offset = self.indents[index + 1:].index(self.indents[index])  # distance between indent start and end
                detachment_index = index + next_same_indent_offset  # index of end bracket, insertion occurs before this value

                if self.indents[index] > self.indents[detachment_index + 2]:  # if moving out of surrounding indent block
                    for ii in range(index, detachment_index + 1):
                        self.indents[ii] -= 1  # decrease indent of entire indent block
                elif self.indents[index] < self.indents[detachment_index + 2]:  # if moving into surrounding indent block
                    for ii in range(index, detachment_index + 1):
                        self.indents[ii] += 1  # increase indent of entire indent block
                for indent_index in range(index, detachment_index):
                    self.set_indent(indent_index)  # reset indents of indent block

            else:  # move single command row
                if self.indents[index] != self.indents[index + 2]:
                    self.indents[index] = self.indents[index + 2]  # set indent to proceeding
                    self.set_indent(index)

            self.vbox_edit.Detach(detachment_index + 1)
            self.vbox_edit.Insert(index, self.edit_row_container_sizers[detachment_index + 1], 0, wx.EXPAND)

            for list_to_reorder in self.tracker_lists:
                list_to_reorder.insert(index, list_to_reorder.pop(detachment_index + 1))

            self.refresh_move_buttons()
            self.edit.Thaw()

    def set_indent(self, indent_index):
        matching_widget_in_edit_row(self.edit_row_widget_sizers[indent_index], 'indent_text').SetLabel(self.indents[indent_index] * 20 * ' ')
        self.Layout()

    def refresh_move_buttons(self):
        for sizer_index, sizer_indiv in enumerate(self.edit_row_container_sizers):
            if sizer_index == 0:  # top-most command
                self.show_move_button(sizer_indiv, 'up', False)
                self.show_move_button(sizer_indiv, 'down', True)

            elif sizer_index == len(self.lines) - 1:  # bottom-most command
                self.show_move_button(sizer_indiv, 'up', True)
                self.show_move_button(sizer_indiv, 'down', False)

            else:
                self.show_move_button(sizer_indiv, 'up', True)
                self.show_move_button(sizer_indiv, 'down', True)

        # hide move down button of indent block start if nothing below indent block
        if self.indents[-2:] != [0, 0]:
            indent_block_start_index = len(self.indents[:-2]) - 1 - self.indents[:-2][::-1].index(0)  # index of last zero before indent block
            self.show_move_button(self.edit_row_container_sizers[indent_block_start_index], 'down', False)

        self.Layout()

    def command_combobox_change(self, sizer, event):
        self.Freeze()
        index = self.edit_row_widget_sizers.index(sizer)
        new_action = event.GetString()
        line_orig = self.lines[index]
        line = line_orig.lower().strip()
        line_first_word = line.split(' ')[0]

        old_coords = self.default_coords
        old_action = ''
        if line.replace(' ', '')[0] == '#':
            old_action = 'Comment'

        elif '-mouse' in line_first_word:
            old_action = 'Mouse button'
            old_coords = coords_of(line)

        elif 'type:' in line_first_word:
            old_action = 'Type'

        elif 'wait' in line_first_word:
            old_action = 'Wait'

        elif 'hotkey' in line_first_word:
            old_action = 'Hotkey'

        elif 'key' in line_first_word:
            key = line.split(' ')[1]
            if key in [x.lower() for x in self.software_info.special_keys]:
                old_action = 'Special key'

            elif key in [x.lower() for x in self.software_info.function_keys]:
                old_action = 'Function key'

            elif key in [x.lower() for x in self.software_info.media_keys]:
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

        elif ('assign' in line_first_word) and ('{{~' in line) and ('~}}' in line):
            old_action = 'Assign'

        elif ('if' in line_first_word) and ('{{~' in line) and ('~}}' in line):
            old_action = 'Conditional'

        if old_action == new_action:  # do nothing as not to reset existing parameters
            return

        # determine index of command combobox to hide all widgets after it
        command_cb_index = 0
        for sizeritem in sizer.GetChildren():
            widget = sizeritem.GetWindow()
            if isinstance(widget, wx.ComboBox):
                if widget.GetName() == 'command':
                    command_cb_index = sizer.GetChildren().index(sizeritem)
                    break

        # hide all widgets after command combobox
        for ii in reversed(range(command_cb_index + 2, len(sizer.GetChildren()))):
            sizer.GetChildren()[ii].Show(False)
            sizer.Remove(ii)

        self.no_right_spacer = False

        if new_action == 'Comment':
            self.lines[index] = '#'
            self.create_comment_row(self.lines[index], sizer)

        elif new_action == 'Mouse button':
            self.lines[index] = f'Left-mouse click at {old_coords}'
            self.create_mouse_row(self.lines[index].lower(), sizer)

        elif new_action == 'Type':
            self.lines[index] = 'Type:'
            self.create_type_row(self.lines[index], sizer)

        elif new_action == 'Wait':
            self.lines[index] = 'Wait'
            self.create_wait_row(self.lines[index].lower(), sizer)

        elif new_action == 'Special key':
            self.lines[index] = 'Key Backspace Tap'
            self.create_key_row(self.lines[index].lower(), sizer)

        elif new_action == 'Function key':
            self.lines[index] = 'Key F1 Tap'
            self.create_key_row(self.lines[index].lower(), sizer)

        elif new_action == 'Media key':
            self.lines[index] = 'Key PlayPause Tap'
            self.create_key_row(self.lines[index].lower(), sizer)

        elif new_action == 'Hotkey':
            self.lines[index] = 'Hotkey'
            self.create_hotkey_row(self.lines[index].lower(), sizer)

        elif new_action == 'Mouse-move':
            self.lines[index] = f'Mouse-move to {old_coords}'
            self.create_mousemove_row(self.lines[index].lower(), sizer)

        elif new_action == 'Double-click':
            self.lines[index] = f'Double-click at {old_coords}'
            self.create_multi_click_row(self.lines[index].lower(), sizer)

        elif new_action == 'Triple-click':
            self.lines[index] = f'Triple-click at {old_coords}'
            self.create_multi_click_row(self.lines[index].lower(), sizer)

        elif new_action == 'Assign':
            self.lines[index] = 'Assign {{~Var~}}=value'
            self.variables['Var'] = 'value'
            self.create_assign_var_row(self.lines[index], sizer)

        elif new_action == 'Conditional':
            self.lines[index] = 'If {{~Var~}} equals ~value~ {'
            self.create_conditional_row(self.lines[index], sizer)
            self.indents[index+1] += 1

            # add end of indent block
            self.lines.insert(index+1, '}')
            self.create_command_sizer(index+1, self.lines[index+1])
            self.vbox_edit.Layout()

        self.create_delete_x_btn(sizer)

        if old_action in ['Conditional', 'Loop']:
            # delete end bracket for associated block
            index_of_end_bracket = index + [line.strip() for line in self.lines[index:]].index('}')  # index of start in list plus index of end in sublist
            self.delete_command(self.edit_row_widget_sizers[index_of_end_bracket])

            # decrease indents for associated block
            for indent_index in range(index+1, index_of_end_bracket):
                self.indents[indent_index] -= 1
                self.set_indent(indent_index)

        self.Layout()
        self.Thaw()

    def mouse_command_change(self, sizer, event):
        index = self.edit_row_widget_sizers.index(sizer)
        command_change = event.GetString()  # can be mouse_button change or mouse_action change

        if command_change == 'Left':
            self.lines[index] = re.compile(re.escape('right'), re.IGNORECASE).sub('Left', self.lines[index])

        elif command_change == 'Right':
            self.lines[index] = re.compile(re.escape('left'), re.IGNORECASE).sub('Right', self.lines[index])

        elif command_change in self.software_info.mouse_actions:  # click, press, or release
            for replace_word in [x for x in self.software_info.mouse_actions if
                                 x != command_change]:  # loop through remaining actions
                self.lines[index] = re.compile(re.escape(replace_word), re.IGNORECASE).sub(command_change.lower(),
                                                                                           self.lines[index])

    def coord_change(self, sizer, event, x=None, y=None):
        command_change = event.GetString()
        index = self.edit_row_widget_sizers.index(sizer)
        text_ctrl = event.GetEventObject()
        text_ctrl.SetForegroundColour(wx.BLACK)
        # find desired element by looping through all sizer children and filtering children with None windows and then the window with desired name
        error_static_text = matching_widget_in_edit_row(sizer, 'error_display')
        error_static_text.SetLabel('')

        # validate input and display feedback
        try:
            if not command_change.isdecimal() and command_change:
                raise ValueError()
            line_split_on_comma = self.lines[index].split(',')
            if x:
                if command_change:
                    x_coord = command_change
                else:
                    x_coord = '0'
                if int(x_coord) > display_size[0]:
                    raise ValueError()
                self.lines[index] = f'{line_split_on_comma[0].split("(")[0]}({x_coord},{line_split_on_comma[1]}'

            elif y:
                if command_change:
                    y_coord = command_change
                else:
                    y_coord = '0'
                if int(y_coord) > display_size[1]:
                    raise ValueError()
                self.lines[index] = f'{line_split_on_comma[0]}, {y_coord})'

        except ValueError:
            text_ctrl.SetForegroundColour(wx.RED)
            # not catastrophic if mouse is moved to coordinates that are out of bounds of the display size
            if x:
                error_msg = f'The max X value is {display_size[0]} px.'
            elif y:
                error_msg = f'The max Y value is {display_size[1]} px.'
            else:
                error_msg = f'The maximum coordinates are {display_size} px.'
            error_static_text.SetLabel(error_msg)
            self.command_row_error = True
            event.Skip()

    def text_change(self, sizer, event, command_type):
        index = self.edit_row_widget_sizers.index(sizer)
        if command_type == 'type':
            self.lines[index] = f'Type:{event.GetString()}'
        elif command_type == 'comment':
            self.lines[index] = f'#{event.GetString()}'
        elif command_type == 'assign_var_name':
            old_variable_name = variable_name_in(self.lines[index])
            new_variable_name = event.GetString()
            variable_value = assignment_variable_value_in(self.lines[index])

            self.lines[index] = f'Assign {{{{~{new_variable_name}~}}}}={variable_value}'

            self.variables.pop(old_variable_name, None)  # remove old variable
            self.variables[new_variable_name] = variable_value  # add new variable
        elif command_type == 'assign_var_value':
            variable_name = variable_name_in(self.lines[index])
            new_variable_value = event.GetString()

            self.lines[index] = f'Assign {{{{~{variable_name}~}}}}={new_variable_value}'

            self.variables[variable_name] = new_variable_value
        elif command_type == 'conditional_var_name':
            variable_name = event.GetString()
            self.lines[index] = f'If {{{{~{variable_name}~}}}} {conditional_operation_in(self.lines[index], self.conditional_operations)} ~{conditional_comparison_in(self.lines[index])}~ {{'
            print(self.lines[index])
        elif command_type == 'conditional_comparison_operator':
            comparison_operator = event.GetString()
            self.lines[index] = f'If {{{{~{variable_name_in(self.lines[index])}~}}}} {comparison_operator} ~{conditional_comparison_in(self.lines[index])}~ {{'
            print(self.lines[index])
        elif command_type == 'conditional_comparison_value':
            comparison_value = event.GetString()
            self.lines[index] = f'If {{{{~{variable_name_in(self.lines[index])}~}}}} {conditional_operation_in(self.lines[index], self.conditional_operations)} ~{comparison_value}~ {{'
            print(self.lines[index])

        event.Skip()

    def wait_change(self, sizer, event):
        index = self.edit_row_widget_sizers.index(sizer)
        command_change = event.GetString()
        text_ctrl = event.GetEventObject()
        text_ctrl.SetMaxLength(0)  # discards previous max length assignment
        text_ctrl.SetForegroundColour(wx.BLACK)
        # find desired element by looping through all sizer children and filtering children with None windows and then the window with desired name
        error_static_text = matching_widget_in_edit_row(sizer, 'error_display')
        error_static_text.SetForegroundColour(wx.RED)
        error_static_text.SetLabel('')
        too_long = False

        # validate input and display feedback
        intervals = (
            ('days', 86400),  # 60 * 60 * 24
            ('hrs', 3600),  # 60 * 60
            ('mins', 60),
            ('secs', 1),
        )

        def verbalize_time(seconds, granularity=4):
            result = []
            for name, count in intervals:
                value = seconds // count
                if value:
                    seconds -= value * count
                    if value == 1:
                        name = name.rstrip('s')
                    # result.append("{} {}".format(value, name))
                    result.append(f'{int(value)} {name}')
            return ', '.join(result[:granularity])

        try:
            wait_time = float(command_change)
            if wait_time > 604800:  # more than a week
                error_static_text.SetLabel('The max wait time is one week.')
                too_long = True
                raise ValueError
            elif wait_time > 60:  # more than a day
                error_static_text.SetLabel(verbalize_time(wait_time))
                error_static_text.SetForegroundColour(wx.BLACK)
            self.lines[index] = f'Wait {float_in(command_change)}'
        except ValueError:
            if command_change:  # if the wait entry is not empty
                text_ctrl.SetForegroundColour(wx.RED)
                if not too_long:
                    error_static_text.SetLabel('Invalid number.')
                if text_ctrl.GetValue() != '.':
                    text_ctrl.SetMaxLength(text_ctrl.GetLineLength(0))
                self.command_row_error = True
                self.lines[index] = f'Wait {float_in(command_change)}'
            else:
                self.lines[index] = 'Wait 0'

    def key_change(self, sizer, event):
        index = self.edit_row_widget_sizers.index(sizer)
        new_key = event.GetString()
        old_key = self.lines[index].split(' ')[1]
        self.lines[index] = self.lines[index].replace(old_key, new_key)

    def key_action_change(self, sizer, event):
        index = self.edit_row_widget_sizers.index(sizer)
        new_action = event.GetString()
        old_action = self.lines[index].split(' ')[2]
        self.lines[index] = self.lines[index].replace(old_action, new_action)

    def hotkey_change(self, sizer, _):
        index = self.edit_row_widget_sizers.index(sizer)

        # only cycle through last number of comboboxes because only they are the hotkey inputs
        combination = [child.GetWindow().GetStringSelection() for child in list(sizer.GetChildren()) if
                       isinstance(child.GetWindow(), wx.ComboBox)][-self.num_hotkeys::]

        combination = eliminate_duplicates(combination)

        try:
            combination.remove('')  # remove blank hotkey placeholders
        except ValueError:
            pass

        self.lines[index] = f'Hotkey {" + ".join(combination)}'

    def on_record(self):

        class RecordDialog(wx.Dialog):
            def __init__(self, parent, caption):
                wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)
                self.parent = parent
                self.SetTitle(caption)
                self.SetIcon(wx.Icon(self.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.SetBackgroundColour('white')

                # setup sizers
                self.vbox = wx.BoxSizer(wx.VERTICAL)
                self.hbox_options = wx.BoxSizer(wx.HORIZONTAL)

                self.some_sleep_thresh = 0.2

                # recording pause input
                self.sleep_sizer = wx.StaticBoxSizer(wx.StaticBox(self, label='Record pause'), wx.VERTICAL)  # ---------

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
                # ------------------------------------------------------------------------------------------------------
                self.hbox_options.AddSpacer(5)

                # recording method input
                self.record_mthd = wx.RadioBox(self, label='Method', choices=['Overwrite', 'Append'], majorDimension=1,
                                               style=wx.RA_SPECIFY_COLS)
                self.record_mthd.SetItemToolTip(0, 'Erase existing data')
                self.record_mthd.SetItemToolTip(1, 'Add to end of existing data')
                self.hbox_options.Add(self.record_mthd, 0, wx.ALL, 5)

                self.vbox.Add(self.hbox_options, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
                self.vbox.AddSpacer(10)

                # add buttons
                self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
                self.vbox.Add(self.btns, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

                self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                self.vbox_outer.Add(self.vbox, 0, wx.ALL, 10)
                self.SetSizerAndFit(self.vbox_outer)
                self.Center()

            def record_some_sleep_pressed(self):
                self.some_sleep_thresh.Enable(True)

            def not_some_sleep_pressed(self):
                self.some_sleep_thresh.Enable(False)

        record_dlg = RecordDialog(self, f'Record - {self.workflow_name}')

        if record_dlg.ShowModal() == wx.ID_OK:

            class RecordCtrlCounterDialog(wx.Dialog):
                def __init__(self, parent, caption, parent_dialog):
                    wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)
                    self.SetTitle(caption)
                    self.SetIcon(wx.Icon(parent.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                    self.SetBackgroundColour('white')
                    self.parent = parent
                    self.done = False

                    self.vbox = wx.BoxSizer(wx.VERTICAL)

                    # add main directions
                    self.directions_a = wx.StaticText(self,
                                                      label=f'Start{self.parent.software_info.start_stop_directions}')
                    change_font(self.directions_a, size=14)
                    self.vbox.Add(self.directions_a, 0, wx.ALIGN_CENTER_HORIZONTAL)

                    self.vbox.AddSpacer(30)

                    # add countdown
                    self.hbox_countdown = wx.BoxSizer(wx.HORIZONTAL)  # ------------------------------------------------

                    self.countdown_dark = wx.StaticText(self, label=parent.workflow_name)
                    change_font(self.countdown_dark, size=22)
                    self.hbox_countdown.Add(self.countdown_dark)
                    self.countdown_dark.Show(False)

                    self.countdown_light = wx.StaticText(self, label=parent.workflow_name)
                    change_font(self.countdown_light, size=22, color=3 * (150,))
                    self.hbox_countdown.Add(self.countdown_light)
                    self.countdown_light.Show(False)

                    self.vbox.Add(self.hbox_countdown, 0, wx.ALIGN_CENTER_HORIZONTAL)
                    # --------------------------------------------------------------------------------------------------

                    self.vbox.AddSpacer(20)

                    # add main status message
                    self.recording_message_a = wx.StaticText(self, label='Now recording clicks and keypresses')
                    change_font(self.recording_message_a, size=13, color=(170, 20, 20))
                    self.vbox.Add(self.recording_message_a, 0, wx.ALIGN_CENTER_HORIZONTAL)
                    self.recording_message_a.Show(False)

                    self.vbox.AddSpacer(5)

                    # add secondary status message
                    self.recording_message_b = wx.StaticText(self, label='Left control key: record mouse position')
                    change_font(self.recording_message_b, size=10, color=(170, 20, 20))
                    self.vbox.Add(self.recording_message_b, 0, wx.ALIGN_CENTER_HORIZONTAL)
                    self.recording_message_b.Show(False)

                    # add completion spacer
                    self.spacer_a = wx.StaticText(self, label='')
                    change_font(self.spacer_a, size=5)
                    self.vbox.Add(self.spacer_a, 0, wx.ALIGN_CENTER_HORIZONTAL)
                    self.spacer_a.Show(False)

                    # add finish button
                    self.finish_btn = wx.Button(self, label='Finish')
                    self.finish_btn.Bind(wx.EVT_BUTTON, self.finish)
                    self.vbox.Add(self.finish_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EAST | wx.WEST, 100)
                    self.finish_btn.Show(False)

                    # add in-action spacer
                    self.spacer_b = wx.StaticText(self, label='')
                    change_font(self.spacer_b, size=20)
                    self.vbox.Add(self.spacer_b, 0, wx.ALIGN_CENTER_HORIZONTAL)
                    self.spacer_b.Show(False)

                    self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                    self.vbox_outer.Add(self.vbox, 0, wx.NORTH | wx.WEST | wx.EAST, 50)
                    self.SetSizerAndFit(self.vbox_outer)
                    self.Position = (parent_dialog.Position[0] + ((parent_dialog.Size[0] - self.Size[0]) / 2),
                                     parent_dialog.Position[1])

                    self.Connect(-1, -1, int(EVT_RESULT_ID),
                                 self.read_thread_event_input)  # Process message events from threads
                    self.listener_thread = ListenerThread(self, record=True)
                    self.listener_thread.start()
                    self.Bind(wx.EVT_CLOSE, self.close_window)

                def read_thread_event_input(self, event):
                    """Show Result status."""
                    if event.data is None:
                        # Thread aborted (since None return)
                        self.countdown_light.SetLabel('Some error occurred')
                        self.countdown_light.Show(True)
                    else:
                        # Process message events
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
                            self.countdown_dark.SetForegroundColour((170, 20, 20))
                            self.directions_a.SetLabel(f'Stop{self.parent.software_info.start_stop_directions}')
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
                            change_font(self.countdown_dark, size=22)
                            self.recording_message_a.Show(False)
                            self.recording_message_b.Show(False)
                            self.spacer_a.Show(True)
                            self.finish_btn.Show(True)
                            self.done = True

                        self.vbox.Layout()
                        self.vbox_outer.Layout()
                        self.SetSizerAndFit(self.vbox_outer)
                        if self.done:
                            self.Raise()
                            self.position_old = self.GetPosition()
                            self.size_old = self.GetSize()
                            self.Position = (self.position_old[0] + ((self.size_old[0] - self.Size[0]) / 2),
                                             self.position_old[1])
                        self.Fit()

                def finish(self, _):
                    lines_recorded = self.listener_thread.abort()
                    if lines_recorded:
                        self.parent.lines = lines_recorded
                        self.parent.create_edit_panel()
                    else:
                        # raise warning if no actions recorded
                        wx.MessageDialog(self, 'No actions detected nor recorded.', 'Warning',
                                         wx.OK | wx.ICON_WARNING).ShowModal()
                    self.close_window()

                def close_window(self, _=None):
                    self.listener_thread.abort()
                    self.parent.Layout()
                    self.Destroy()

            RecordCtrlCounterDialog(self, f'Record - {self.workflow_name}', record_dlg).ShowModal()

    def on_execute(self):

        class ExecuteDialog(wx.Dialog):
            def __init__(self, parent, caption):
                wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)  # | wx.RESIZE_BORDER)
                self.parent = parent
                self.SetTitle(caption)
                self.SetIcon(wx.Icon(self.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.SetBackgroundColour('white')

                self.vbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Options'), wx.VERTICAL)
                self.vbox.AddSpacer(10)

                # execution pause input
                self.hbox_pause = wx.BoxSizer(wx.HORIZONTAL)  # --------------------------------------------------------

                self.checkbox_pause = wx.CheckBox(self, label=' Pause between commands: ')
                self.checkbox_pause.SetValue(True)
                self.checkbox_pause.Bind(wx.EVT_CHECKBOX, self.checkbox_pause_pressed)
                self.hbox_pause.Add(self.checkbox_pause, 0, wx.ALIGN_CENTER_VERTICAL)

                self.execute_pause_input = PlaceholderTextCtrl(self, wx.ID_ANY, placeholder='0.2', size=wx.Size(50, -1),
                                                               style=wx.TE_CENTER)
                self.hbox_pause.Add(self.execute_pause_input, 0, wx.ALIGN_CENTER_VERTICAL)

                self.hbox_pause.Add(wx.StaticText(self, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
                self.vbox.Add(self.hbox_pause, 0, wx.EAST | wx.WEST, 10)
                # ------------------------------------------------------------------------------------------------------

                self.vbox.AddSpacer(20)

                # Mouse duration input
                self.hbox_mouse_dur = wx.BoxSizer(wx.HORIZONTAL)  # ----------------------------------------------------

                self.checkbox_mouse_dur = wx.CheckBox(self, label=' Mouse command duration: ')
                self.checkbox_mouse_dur.SetValue(True)
                self.checkbox_mouse_dur.Bind(wx.EVT_CHECKBOX, self.checkbox_mouse_dur_pressed)
                self.hbox_mouse_dur.Add(self.checkbox_mouse_dur, 0, wx.ALIGN_CENTER_VERTICAL)

                self.execute_mouse_dur_input = PlaceholderTextCtrl(self, wx.ID_ANY, placeholder='1',
                                                                   size=wx.Size(50, -1),
                                                                   style=wx.TE_CENTER)
                self.hbox_mouse_dur.Add(self.execute_mouse_dur_input, 0, wx.ALIGN_CENTER_VERTICAL)

                self.hbox_mouse_dur.Add(wx.StaticText(self, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
                self.vbox.Add(self.hbox_mouse_dur, 0, wx.EAST | wx.WEST, 10)
                # ------------------------------------------------------------------------------------------------------

                self.vbox.AddSpacer(20)

                # Text type interval duration input
                self.hbox_type_interval = wx.BoxSizer(wx.HORIZONTAL)  # ------------------------------------------------

                self.checkbox_type_interval = wx.CheckBox(self, label=' Interval between text character outputs: ')
                self.checkbox_type_interval.SetValue(True)
                self.checkbox_type_interval.Bind(wx.EVT_CHECKBOX, self.checkbox_type_interval_pressed)
                self.hbox_type_interval.Add(self.checkbox_type_interval, 0, wx.ALIGN_CENTER_VERTICAL)

                self.execute_type_interval_input = PlaceholderTextCtrl(self, wx.ID_ANY, placeholder='0.05',
                                                                       size=wx.Size(50, -1)
                                                                       , style=wx.TE_CENTER)
                self.hbox_type_interval.Add(self.execute_type_interval_input, 0, wx.ALIGN_CENTER_VERTICAL)

                self.hbox_type_interval.Add(wx.StaticText(self, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
                self.vbox.Add(self.hbox_type_interval, 0, wx.EAST | wx.WEST, 10)
                # ------------------------------------------------------------------------------------------------------

                self.vbox.AddSpacer(10)

                self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)

                self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                self.vbox_outer.Add(wx.StaticText(self, label='Uncheck option(s) for fastest execution'), 0,
                                    wx.ALIGN_RIGHT | wx.NORTH | wx.EAST | wx.WEST, 20)
                self.vbox_outer.Add(self.vbox, 0, wx.EAST | wx.WEST | wx.SOUTH, 20)
                self.vbox_outer.Add(self.btns, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, 15)
                self.SetSizerAndFit(self.vbox_outer)
                self.Center()

            def checkbox_pause_pressed(self, _):
                self.execute_pause_input.Enable(self.checkbox_pause.GetValue())

            def checkbox_mouse_dur_pressed(self, _):
                self.execute_mouse_dur_input.Enable(self.checkbox_mouse_dur.GetValue())

            def checkbox_type_interval_pressed(self, _):
                self.execute_type_interval_input.Enable(self.checkbox_type_interval.GetValue())

        execute_dlg = ExecuteDialog(self, f'Execute - {self.workflow_name}')

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

            class ExecuteCtrlCounterDialog(wx.Dialog):
                def __init__(self, parent, caption, parent_dialog):
                    wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)
                    self.SetTitle(caption)
                    self.SetIcon(wx.Icon(parent.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                    self.SetBackgroundColour('white')
                    self.parent = parent
                    self.done = False

                    self.vbox = wx.BoxSizer(wx.VERTICAL)

                    # add main directions
                    self.directions_a = wx.StaticText(self,
                                                      label=f'Start{self.parent.software_info.start_stop_directions}')
                    change_font(self.directions_a, size=14)
                    self.vbox.Add(self.directions_a, 0, wx.ALIGN_CENTER_HORIZONTAL)

                    self.vbox.AddSpacer(10)

                    # add secondary directions
                    self.directions_b = wx.StaticText(self,
                                                      label='Stop: Move the mouse to the upper-left screen corner')
                    change_font(self.directions_b, size=14, color=(170, 20, 20))
                    self.vbox.Add(self.directions_b, 0, wx.ALIGN_CENTER_HORIZONTAL)

                    self.vbox.AddSpacer(30)

                    self.hbox_countdown = wx.BoxSizer(wx.HORIZONTAL)

                    # add countdown
                    self.countdown_dark = wx.StaticText(self, label=parent.workflow_name)  # ---------------------------
                    change_font(self.countdown_dark, size=22)
                    self.hbox_countdown.Add(self.countdown_dark)
                    self.countdown_dark.Show(False)

                    self.countdown_light = wx.StaticText(self, label=parent.workflow_name)
                    change_font(self.countdown_light, size=22, color=3 * (150,))
                    self.hbox_countdown.Add(self.countdown_light)
                    self.countdown_light.Show(False)

                    self.vbox.Add(self.hbox_countdown, 0, wx.ALIGN_CENTER_HORIZONTAL)
                    # --------------------------------------------------------------------------------------------------

                    self.vbox.AddSpacer(20)

                    # add status message
                    self.executing_message_a = wx.StaticText(self, label='Now executing clicks and keypresses')
                    change_font(self.executing_message_a, size=13, color=(20, 120, 20))
                    self.vbox.Add(self.executing_message_a, 0, wx.ALIGN_CENTER_HORIZONTAL)
                    self.executing_message_a.Show(False)

                    # add completion spacer
                    self.spacer_a = wx.StaticText(self, label='')
                    change_font(self.spacer_a, size=5)
                    self.vbox.Add(self.spacer_a, 0, wx.ALIGN_CENTER_HORIZONTAL)
                    self.spacer_a.Show(False)

                    # add finish button
                    self.finish_btn = wx.Button(self, label='Finish')
                    self.finish_btn.Bind(wx.EVT_BUTTON, self.close_window)
                    self.vbox.Add(self.finish_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EAST | wx.WEST, 100)
                    self.finish_btn.Show(False)

                    # add in-action spacer
                    self.spacer_b = wx.StaticText(self, label='')
                    change_font(self.spacer_b, size=20)
                    self.vbox.Add(self.spacer_b, 0, wx.ALIGN_CENTER_HORIZONTAL)
                    self.spacer_b.Show(False)

                    self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                    self.vbox_outer.Add(self.vbox, 0, wx.NORTH | wx.WEST | wx.EAST, 50)
                    self.SetSizerAndFit(self.vbox_outer)
                    self.Position = (parent_dialog.Position[0] + ((parent_dialog.Size[0] - self.Size[0]) / 2),
                                     parent_dialog.Position[1])

                    # Process message events from threads
                    self.Connect(-1, -1, int(EVT_RESULT_ID), self.read_thread_event_input)
                    self.listener_thread = ListenerThread(self, listen_to_key=True, listen_to_mouse=False)
                    self.listener_thread.start()
                    self.Bind(wx.EVT_CLOSE, self.close_window)

                def start_execution_thread(self):

                    class ExecutionThread(threading.Thread):
                        """Worker Thread Class."""

                        def __init__(self, parent):
                            """Init Worker Thread Class."""
                            threading.Thread.__init__(self, daemon=True)
                            self.parent = parent
                            # global execution_thread
                            # execution_thread = self

                        def run(self):
                            """Run Worker Thread."""

                            drag_duration_scale = math.hypot(pyauto.size().width, pyauto.size().width)
                            lines = self.parent.parent.lines
                            type_interval = self.parent.parent.execution_type_intrv
                            mouse_duration = self.parent.parent.execution_mouse_dur

                            mouse_down_coords = [0, 0]
                            variables = dict()
                            pyauto.PAUSE = self.parent.parent.execution_pause
                            self.keep_running = True

                            try:
                                def on_move(x, y):
                                    """Process click for mouse listener for ExecutionThread instances."""
                                    if x < 5 and y < 5:
                                        self.keep_running = False

                                self.mouse_listener = mouse.Listener(
                                    on_move=on_move)  # monitor mouse position to stop execution if failsafe detected
                                self.mouse_listener.start()

                                time.sleep(0.5)  # wait for last activating CTRL key to be released fully

                                for line_orig in lines:
                                    if self.keep_running:  # only run when running
                                        line = line_orig.lower()

                                        if 'type' in line:  # 'type' command execution should be checked-for first because it may contain other command keywords
                                            pyauto.typewrite(
                                                re.compile(re.escape('type:'), re.IGNORECASE).sub('', line_orig),
                                                interval=type_interval)

                                        elif 'wait' in line:
                                            tot_time = float_in(line)
                                            time_floored = math.floor(
                                                0.05 * math.floor(tot_time / 0.05))  # round down to nearest 0.05
                                            for half_sec_interval in range(
                                                    20 * time_floored):  # loop through each 0.05 second and if still running
                                                if self.keep_running:
                                                    time.sleep(0.05)
                                            time.sleep(
                                                tot_time - time_floored)  # wait additional time unaccounted for in rounding

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
                                                drag_dist = math.hypot(mouse_down_coords[0] - coords[0],
                                                                       mouse_down_coords[1] - coords[1])
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
                                                key = line.replace('key', '').replace('press', '').replace(' ', '')
                                                pyauto.keyDown(key)
                                            elif 'release' in line:
                                                key = line.replace('key', '').replace('release', '').replace(' ', '')
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

                                        elif ('assign' in line) and ('{{~' in line) and ('~}}' in line):
                                            variables[variable_name_in(line)] = assignment_variable_value_in(line)
                                            print(variables)

                            except pyauto.FailSafeException:
                                self.keep_running = False

                            try:
                                if not self.keep_running:
                                    wx.PostEvent(self.parent, ResultEvent('Failsafe triggered'))
                                else:
                                    wx.PostEvent(self.parent, ResultEvent('Completed!'))
                            except RuntimeError:
                                print('Runtime error code kTPbmaAW66')
                                raise SystemError('Runtime error code kTPbmaAW66')

                        def abort(self):
                            self.mouse_listener.stop()
                            self.keep_running = False
                            pyauto.FAILSAFE = False
                            pyauto.PAUSE = 0.001
                            for key in self.parent.parent.software_info.special_keys:  # release any problematic keys that may still be pressed
                                pyauto.keyUp(key)
                            for button in self.parent.parent.software_info.mouse_buttons:
                                pyauto.mouseUp(button=button.lower())
                            pyauto.PAUSE = self.parent.parent.execution_pause
                            pyauto.FAILSAFE = True

                    self.execution_thread = ExecutionThread(self)
                    self.execution_thread.start()

                def read_thread_event_input(self, event):
                    """Show Result status."""
                    if event.data is None:
                        # Thread aborted (since None return)
                        self.countdown_light.SetLabel('Some error occurred')
                        self.countdown_light.Show(True)
                    else:
                        # Process message events
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
                            self.countdown_dark.SetForegroundColour((20, 120, 20))
                            self.countdown_light.SetLabel('')
                            self.countdown_light.Show(False)
                            self.executing_message_a.Show(True)
                            self.start_execution_thread()

                        elif event.data == 'Stopping in 3':
                            self.countdown_light.SetLabel(' 2 1')

                        elif event.data == 'Stopping in 3 2':
                            self.countdown_light.SetLabel(' 1')

                        elif event.data == 'Completed!':
                            self.execution_thread.abort()
                            self.directions_a.Show(False)
                            self.directions_b.Show(False)
                            self.countdown_light.SetLabel('')
                            self.countdown_light.Show(False)
                            change_font(self.countdown_dark, size=22)
                            self.executing_message_a.Show(False)
                            self.spacer_a.Show(True)
                            self.finish_btn.Show(True)
                            self.done = True

                        elif event.data == 'Failsafe triggered':
                            self.execution_thread.abort()
                            self.directions_a.Show(False)
                            self.directions_b.SetLabel('Top-Left Corner Failsafe Triggered')
                            self.countdown_light.SetLabel('')
                            self.countdown_light.Show(False)
                            self.countdown_dark.SetLabel('Execution Stopped')
                            change_font(self.countdown_dark, size=22, style=wx.ITALIC, color=(170, 20, 20))
                            self.executing_message_a.Show(False)
                            self.spacer_a.Show(True)
                            self.finish_btn.Show(True)
                            self.done = True

                        self.vbox.Layout()
                        self.vbox_outer.Layout()
                        self.SetSizerAndFit(self.vbox_outer)
                        if self.done:
                            self.Raise()
                            self.position_old = self.GetPosition()
                            self.size_old = self.GetSize()
                            self.Position = (self.position_old[0] + ((self.size_old[0] - self.Size[0]) / 2),
                                             self.position_old[1])
                        self.Fit()

                def close_window(self, _):
                    self.keep_running = False
                    try:
                        self.listener_thread.abort()
                    except AttributeError:
                        pass
                    try:
                        self.execution_thread.abort()
                    except AttributeError:
                        pass
                    self.Destroy()

            ExecuteCtrlCounterDialog(self, f'Execute - {self.workflow_name}', execute_dlg).ShowModal()

    @staticmethod
    def show_move_button(command_row_sizeritem, up_down, show=True):
        """Show move bitmap button."""

        if up_down == 'up':
            up_down_index = 0
        elif up_down == 'down':
            up_down_index = -1
        else:
            raise ValueError('The up_down parameter passed did not match \'up\' nor \'down\'.')

        if len(command_row_sizeritem.GetChildren()) == 1:
            # attempting to show move button of command row of line concluding indent block ("}") but not valid so do nothing
            return
        else:
            return command_row_sizeritem.GetChildren()[0].GetSizer().GetChildren()[1].GetSizer().GetChildren()[up_down_index].GetWindow().Show(show)

    # do_nothing = lambda: None
    @staticmethod
    def do_nothing(_):  # might want to use to redirect scroll inputs
        """Function to bind events to be disabled."""
        pass

    def close_window(self, _=None, quitall=False):
        if self.lines_when_launched != self.lines or self.workflow_name_when_launched != self.workflow_name:
            # confirm save intent when closing with changes
            class SaveDialog(wx.Dialog):
                def __init__(self, parent_win):
                    wx.Dialog.__init__(self, parent_win, title=f'{parent_win.software_info.name} - Save Changes',
                                       style=wx.DEFAULT_DIALOG_STYLE)
                    self.SetBackgroundColour('white')
                    self.vbox = wx.BoxSizer(wx.VERTICAL)

                    # add save message
                    self.message = wx.StaticText(self, wx.ID_ANY,
                                                 f'Do you want to save changes to \'{parent_win.workflow_name}\'?')
                    change_font(self.message, size=13, color=(35, 75, 160))
                    self.vbox.Add(self.message, 0, wx.ALL, 10)

                    self.vbox.AddSpacer(20)
                    self.vbox.Add(wx.StaticLine(self), 0, wx.EXPAND)

                    # create save buttons
                    self.save_button_panel = wx.Panel(self)
                    self.save_button_panel.BackgroundColour = (240, 240, 240)
                    self.button_array = wx.StdDialogButtonSizer()
                    self.button_array.AddSpacer(100)
                    self.save_btn = wx.Button(self.save_button_panel, wx.ID_OK, label='Save')
                    self.button_array.Add(self.save_btn)
                    self.button_array.AddSpacer(5)
                    self.save_btn = wx.Button(self.save_button_panel, wx.ID_REVERT_TO_SAVED, label='Don\'t Save')
                    self.save_btn.Bind(wx.EVT_BUTTON, self.on_no_save)
                    self.button_array.Add(self.save_btn)
                    self.button_array.AddSpacer(5)
                    self.cancel_btn = wx.Button(self.save_button_panel, wx.ID_CANCEL, label='Cancel')
                    self.button_array.Add(self.cancel_btn)

                    # create button container for color around buttons
                    self.button_container = wx.BoxSizer(wx.HORIZONTAL)
                    self.button_container.Add(self.button_array, 1, wx.EXPAND | wx.ALL, 5)

                    self.save_button_panel.SetSizer(self.button_container)

                    self.vbox.Add(self.save_button_panel, 1, wx.EXPAND)

                    self.SetSizerAndFit(self.vbox)
                    self.Center()

                def on_no_save(self, _):
                    self.EndModal(20)  # terminate dialog with exit code 20

            workflow_path_when_launched = f'{self.parent.workflow_directory}{self.workflow_name_when_launched}.txt'

            save_dlg = SaveDialog(self).ShowModal()
            if save_dlg == wx.ID_OK:
                # write to workflow file
                with open(workflow_path_when_launched, 'w') as record_file:
                    print(f'LINES: {self.lines}')
                    for line in self.lines:
                        record_file.write(f'{line}\n')

                if self.workflow_name_when_launched != self.workflow_name:  # if workflow was renamed
                    workflow_path_new = f'{self.parent.workflow_directory}{self.workflow_name}.txt'
                    os.rename(workflow_path_when_launched, workflow_path_new)
                    self.parent.recent_workflows = eliminate_duplicates(self.parent.recent_workflows)
                    self.parent.recent_workflows.remove(workflow_path_when_launched)
                    self.parent.recent_workflows.insert(0, workflow_path_new)
                    self.parent.update_recent_workflows()
            elif save_dlg == 20:  # 'don't save' button
                pass
            else:  # cancel button
                return

        self.Hide()
        if quitall:
            # close entire application include SelectionFrame
            self.parent.Close(True)
        else:
            # center workflow frame where edit frame is now
            self.parent.Position = (self.Position[0] + ((self.Size[0] - self.parent.Size[0]) / 2),
                                    self.Position[1] + ((self.Size[1] - self.parent.Size[1]) / 2))
            self.parent.Show()
            self.parent.Raise()
            self.parent.Layout()


class SelectionFrame(wx.Frame):
    """Main frame to select workflow."""

    def __init__(self, parent):
        class SoftwareInfo:
            """Object to contain all information about Aldras."""

            def __init__(self):
                self.name = 'Aldras'
                self.version = '2020.1.4 Alpha'
                self.data_directory = 'data/'
                self.icon = f'{self.data_directory}{self.name.lower()}.ico'  # should be data/aldras.ico
                self.png = f'{self.data_directory}{self.name.lower()}.png'  # should be data/aldras.png
                self.copyright = f'2019-2020 {self.name}'
                self.website = f'http://www.{self.name.lower()}.com/'
                self.description = f'{self.name} is a simple and intuitive automation tool that can drastically\nimprove the efficiency of processes with repetitive computer tasks.'
                self.start_stop_directions = ': Press the right control key 3 times'
                self.advanced_edit_guide_description = f'{self.name} is not sensitive capitalization upon ingest,\nplease use whatever convention is most readable for you.'
                self.advanced_edit_guide_command_description = 'Replace the values in the double quotes " ".'
                self.advanced_edit_guide_commands = {
                    '"Left/Right"-mouse "click/press/release" at ("x", "y")': ['Left-mouse click at (284, 531)',
                                                                               'Simulates mouse click, press, or release'],
                    'Type:"text"': ['Type:This report is initiated by John Smith.', 'Simulates text keyboard output'],
                    'Wait "time (seconds)"': ['Wait 0.5', 'Wait for a specified number of seconds'],
                    'Key "key" "tap/press/release"': ['Key Enter Tap',
                                                      'Simulates keyboard key tap, press, or release'],
                    'Hotkey "key 1" + "key 2" + "key 3"': [['Hotkey Ctrl + S', 'Hotkey Ctrl + Shift + Left'],
                                                           'Simulates simultaneous keyboard key presses then releases'],
                    'Mouse-move to ("x", "y")': ['Mouse-move to (284, 531)', 'Simulates mouse movement'],
                    'Double-click at ("x", "y")': ['Double-click at (284, 531)', 'Simulates double left click'],
                    'Triple-click at ("x", "y")': ['Triple-click at (284, 531)', 'Simulates triple left click']
                }
                self.advanced_edit_guide_commands_pro = {
                    'Assign {{~"Variable"~}}="value"': ['Assign {{~Name~}}=John Smith',
                                                        'Assigns value to variable that can be referenced later'],
                }
                self.advanced_edit_guide_commands.update(self.advanced_edit_guide_commands_pro)
                self.advanced_edit_guide_website = f'{self.website}/edit-guide'
                self.commands = ['Mouse button', 'Type', 'Wait', 'Special key', 'Function key', 'Media key', 'Hotkey',
                                 'Mouse-move', 'Double-click', 'Triple-click', 'Comment', 'Assign', 'Conditional',
                                 'Loop']
                self.mouse_buttons = ['Left', 'Right']
                self.mouse_actions = ['Click', 'Press', 'Release']
                self.key_actions = ['Tap', 'Press', 'Release']
                self.coord_width = 40
                self.special_keys = ['Backspace', 'Del', 'Enter', 'Tab', 'Left', 'Right', 'Up', 'Down', 'Home', 'End',
                                     'PageUp', 'PageDown', 'Space', 'Shift', 'Esc', 'Ctrl', 'Alt', 'Win', 'Command',
                                     'Option', 'BrowserBack', 'BrowserForward', 'Insert', 'NumLock', 'PrntScrn',
                                     'ScrollLock']
                self.media_keys = ['PlayPause', 'NextTrack', 'PrevTrack', 'VolumeMute', 'VolumeUp', 'VolumeDown']
                self.function_keys = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
                self.alphanum_keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                                      'Q', 'R',
                                      'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7',
                                      '8', '9',
                                      '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':',
                                      ';', '<',
                                      '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']
                self.all_keys = [''] + self.special_keys + self.alphanum_keys + self.media_keys

        self.software_info = SoftwareInfo()
        wx.Frame.__init__(self, parent, title=f'{self.software_info.name} Automation')
        setup_frame(self)

        # Creates directories if do not exist --------------------------------------------------------------------------
        self.workflow_directory = 'Workflows/'
        if not os.path.exists(self.workflow_directory):
            os.makedirs(self.workflow_directory)

        if not os.path.exists(self.software_info.data_directory):
            os.makedirs(self.software_info.data_directory)

        self.data_directory_recent_workflows = f'{self.software_info.data_directory}recent_workflows.txt'
        try:
            with open(self.data_directory_recent_workflows, 'r') as record_file:
                self.recent_workflows = eliminate_duplicates([line.rstrip('\n') for line in record_file])
        except FileNotFoundError:  # create file if not found
            with open(self.data_directory_recent_workflows, 'w'):
                self.recent_workflows = []
        # --------------------------------------------------------------------------------------------------------------

        # add encompassing panel
        self.workflow_panel = wx.Panel(self)

        # set parameters
        self.margin_y = 25
        self.margin_x = 150
        self.padding_y = 25

        self.vbox = wx.BoxSizer(wx.VERTICAL)  # ------------------------------------------------------------------------

        # add rescaled logo image
        png = wx.Image(self.software_info.png, wx.BITMAP_TYPE_PNG).Scale(150, 150,
                                                                         quality=wx.IMAGE_QUALITY_HIGH)
        self.logo_img = wx.StaticBitmap(self.workflow_panel, wx.ID_ANY, wx.Bitmap(png))
        self.vbox.Add(self.logo_img, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program name text
        self.program_name = wx.StaticText(self.workflow_panel, label=f'{self.software_info.name} Automation')
        change_font(self.program_name, size=18, color=3 * (60,))
        self.vbox.Add(self.program_name, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, self.padding_y)

        # add input field for the workflow name
        self.workflow_name_input = PlaceholderTextCtrl(self.workflow_panel, wx.ID_ANY, placeholder='Workflow',
                                                       size=(200, -1),
                                                       style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_ok, self.workflow_name_input)
        self.vbox.Add(self.workflow_name_input, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, self.padding_y)

        # add recent workflow title
        self.vbox_recent = wx.BoxSizer(wx.VERTICAL)
        self.recent_title = wx.StaticText(self.workflow_panel, label='Recent')
        change_font(self.recent_title, size=10, style=wx.ITALIC, color=3 * (150,))
        self.recent_title.Show(False)  # hide until know there are recent workflows
        self.vbox_recent.Add(self.recent_title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, 5)

        # add recent workflow names
        self.hbox_recent = wx.BoxSizer(wx.HORIZONTAL)
        self.update_recent_workflows()
        self.vbox_recent.Add(self.hbox_recent, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.Add(self.vbox_recent, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.AddSpacer(self.padding_y)
        # --------------------------------------------------------------------------------------------------------------

        # add outer sizer
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox_outer.AddStretchSpacer()
        self.vbox_outer.AddSpacer(self.margin_y)  # north margin
        self.vbox_outer.Add(self.vbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EAST | wx.WEST, self.margin_x)
        self.vbox_outer.AddStretchSpacer()

        # add buttons
        self.button_array = wx.StdDialogButtonSizer()
        self.ok_btn = wx.Button(self.workflow_panel, label='OK')
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        self.button_array.Add(self.ok_btn)
        self.button_array.AddSpacer(5)
        self.exit_btn = wx.Button(self.workflow_panel, label='Exit')
        self.exit_btn.Bind(wx.EVT_BUTTON, self.on_exit)
        self.button_array.Add(self.exit_btn)
        self.vbox_outer.Add(self.button_array, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        # display frame
        self.workflow_panel.SetSizerAndFit(self.vbox_outer)
        self.vbox_outer.SetSizeHints(self)
        self.Bind(wx.EVT_CLOSE, self.close_window)
        self.ok_btn.SetFocus()
        self.Center()
        self.Show()

    def update_recent_workflows(self):
        self.recent_workflows = eliminate_duplicates(self.recent_workflows)
        with open(self.data_directory_recent_workflows, 'w') as record_file:  # add workflow to recent history
            for line in self.recent_workflows[0:10]:
                record_file.write(f'{line}\n')

        self.hbox_recent.ShowItems(show=False)
        self.hbox_recent.Clear(delete_windows=True)

        # show recent workflow title if there are recent workflows
        if self.recent_workflows:
            self.recent_title.Show()

        # create buttons for 3 most recently accessed workflows
        for workflow_path_name in self.recent_workflows[0:3]:
            workflow_name = workflow_path_name.replace('.txt', '').replace(self.workflow_directory, '')
            self.recent_workflow_btn = wx.Button(self.workflow_panel, wx.ID_ANY, label=workflow_name)
            self.recent_workflow_btn.Bind(wx.EVT_BUTTON,
                                          lambda event, workflow_path_trap=workflow_path_name: self.launch_workflow(
                                              workflow_path_trap, recent_launch=True))
            self.hbox_recent.Add(self.recent_workflow_btn)

        self.hbox_recent.ShowItems(show=True)
        self.hbox_recent.Layout()
        self.vbox_recent.Layout()
        self.Layout()

    def on_ok(self, _):
        if self.workflow_name_input.GetValue() == '':
            # error warning if entry is empty
            wx.MessageDialog(self, 'Invalid file name.\nPlease try again.', 'Invalid File Name',
                             wx.OK | wx.ICON_EXCLAMATION).ShowModal()

        else:
            # workflow confirmation if entry is default 'Workflow'
            confirm_workflow_dlg = wx.MessageDialog(None,
                                                    f'Please confirm that "{self.workflow_name_input.GetValue().capitalize()}" is your desired workflow.',
                                                    f'{self.software_info.name} Workflow Confirmation',
                                                    wx.YES_NO | wx.ICON_INFORMATION)

            if confirm_workflow_dlg.ShowModal() == wx.ID_YES:
                self.launch_workflow(
                    workflow_path_name=f'{self.workflow_directory}{self.workflow_name_input.GetValue().capitalize()}.txt')

    def launch_workflow(self, workflow_path_name, recent_launch=False):
        if recent_launch:
            # when launching recent workflow, make sure it still exists and read lines
            try:
                with open(workflow_path_name, 'r') as record_file:
                    pass
            except FileNotFoundError:
                wx.MessageDialog(self,
                                 f'The recent workflow at \'{workflow_path_name}\' no longer exists.\nIt may have been renamed, moved, or deleted.',
                                 'Missing workflow', wx.OK | wx.ICON_WARNING).ShowModal()

                self.recent_workflows = eliminate_duplicates(self.recent_workflows)
                self.recent_workflows.remove(workflow_path_name)
                self.update_recent_workflows()
                return

        self.workflow_name = workflow_path_name.replace('.txt', '').replace(self.workflow_directory, '')
        self.workflow_path_name = workflow_path_name

        # read or create workflow file
        try:
            with open(f'{self.workflow_directory}{self.workflow_name}.txt', 'r') as record_file:
                lines = record_file.readlines()
        except FileNotFoundError:  # create file if not found
            with open(f'{self.workflow_directory}{self.workflow_name}.txt', 'w'):
                lines = []
        lines = [line.replace('\n', '') for line in lines]

        if len(lines) > 100:
            confirm_long_workflow_dlg = wx.MessageDialog(None,
                                                         f'"{self.workflow_name}" has {len(lines)} lines.\n\nWe recommend using loops and other tools to optimize workflows to less than 100 lines to maximize the speed and stability of {self.software_info.name}.\n\nContinue anyway?',
                                                         'Long Workflow Warning',
                                                         wx.YES_NO | wx.ICON_WARNING | wx.CENTRE)

            if confirm_long_workflow_dlg.ShowModal() == wx.ID_NO:
                return

        self.Hide()
        EditFrame(self, lines)

        # add recently launched workflow to history
        self.recent_workflows.insert(0, self.workflow_path_name)

        # update frame
        self.update_recent_workflows()
        self.workflow_panel.SetSizerAndFit(self.vbox_outer)
        self.vbox_outer.SetSizeHints(self)
        self.Fit()

    def on_exit(self, _):
        # trigger close event
        self.Close(True)

    @staticmethod
    def close_window(close_event):
        # handle close event
        try:
            # close monitor frame if open
            global mouse_monitor_frame
            mouse_monitor_frame.Close(True)
        except (AttributeError, RuntimeError):
            pass
        close_event.Skip()

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
    # get system platform
    print(f'system_platform: {system_platform()}')

    # get unique hardware id
    import subprocess
    hardware_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
    print(f'hardware_id: {hardware_id}')

    # get number of cores
    import psutil
    cpu_num_cores = psutil.cpu_count()
    print(f'cpu_num_cores: {cpu_num_cores}')

    # get capslock status on windows
    global capslock
    capslock = bool(ctypes.WinDLL("User32.dll").GetKeyState(0x14))  # TODO test on other platforms

    # global variable needed for threading event receiving
    global EVT_RESULT_ID
    EVT_RESULT_ID = wx.NewIdRef()

    # get display size
    global display_size
    display_size = (
        sum([monitor.width for monitor in get_monitors()]), sum([monitor.height for monitor in get_monitors()]))
    print(f'display_size: {display_size}')
    print()

    global mouse_monitor_frame
    mouse_monitor_frame = None

    app = wx.App(False)
    SelectionFrame(None)
    app.MainLoop()


if __name__ == '__main__':
    global capslock
    global EVT_RESULT_ID
    global display_size
    global mouse_monitor_frame
    main()
