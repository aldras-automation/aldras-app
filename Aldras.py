import ntpath
import os
import re
import sys
import threading
import time
import webbrowser
from platform import system as system_platform

import numpy as np
import pandas as pd
import pyautogui as pyauto
import pyperclip
import requests
import wx
import wx.adv
import wx.grid
import wx.lib.expando
import wx.lib.scrolledpanel
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet
from pynput import keyboard, mouse

from modules.aldras_core import get_system_parameters, float_in, variable_names_in, assignment_variable_value_in, \
    conditional_operation_in, conditional_comparison_in, loop_table_data_from, PlaceholderTextCtrl, \
    textctrl_tab_trigger_nav, coords_of, \
    eliminate_duplicates, block_end_index, exception_handler, show_notification, CharValidator, \
    check_internet_connection
from modules.aldras_settings import import_settings, open_settings
from modules.aldras_threads import ListenerThread, ExecutionThread


def matching_widget_in_edit_row(sizer, name):
    matching_widgets = [child.GetWindow() for child in sizer.GetChildren() if
                        child.GetWindow() and child.GetWindow().GetName() == name]

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
                self.program_copyright = wx.StaticText(self, label=f'Copyright {self.parent.software_info.copyright}')
                self.vbox_top.Add(self.program_copyright, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH, 10)

                self.hbox_btns = wx.BoxSizer(wx.HORIZONTAL)

                # add license button
                self.license_btn = wx.Button(self, label='EULA')
                self.license_btn.SetFocus()
                self.license_btn.Bind(wx.EVT_BUTTON, self.launch_eula)
                self.hbox_btns.Add(self.license_btn)

                self.hbox_btns.AddStretchSpacer()
                self.hbox_btns.AddSpacer(5)
                self.hbox_btns.AddStretchSpacer()

                # add privacy statement button
                self.privacy_btn = wx.Button(self, label='Privacy')
                self.privacy_btn.Bind(wx.EVT_BUTTON,
                                      lambda event: webbrowser.open_new_tab('https://aldras.netlify.com/privacy'))
                self.hbox_btns.Add(self.privacy_btn)

                self.vbox.AddMany([(self.vbox_top, 0, wx.EXPAND | wx.NORTH | wx.EAST | wx.WEST, 40),
                                   (self.hbox_btns, 0, wx.EXPAND | wx.NORTH, 20)])

                self.vbox_outer.Add(self.vbox, 0, wx.ALL, 5)
                self.SetSizerAndFit(self.vbox_outer)
                self.Center()

            def launch_eula(self, event):
                class EULADialog(wx.Dialog):
                    """Frame to display EULA"""

                    def __init__(self, parent):
                        wx.Dialog.__init__(self, parent, title='Aldras: End User License Agreement', name='eula_frame',
                                           style=wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.RESIZE_BORDER)
                        self.SetBackgroundColour(wx.WHITE)
                        self.SetIcon(wx.Icon('data/aldras.ico', wx.BITMAP_TYPE_ICO))  # assign icon

                        # read the EULA license.txt file
                        try:
                            with open('data/license.txt', 'r') as license_file:
                                license_text = ''.join(license_file.readlines())
                        except FileNotFoundError:  # create file if not found
                            license_text = 'License file could be found...\n\nPlease contact us at aldras.netlify.com/contact for EULA information.'

                        vbox_container = wx.BoxSizer(wx.VERTICAL)
                        vbox = wx.BoxSizer(wx.VERTICAL)

                        vbox.AddSpacer(10)

                        title_st = wx.StaticText(self, label='Aldras End User License Agreement')
                        change_font(title_st, size=12)
                        vbox.Add(title_st, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH | wx.SOUTH, 20)

                        eula_text = wx.TextCtrl(self, value=license_text, style=wx.TE_MULTILINE | wx.TE_READONLY)
                        vbox.Add(eula_text, 1, wx.EXPAND | wx.SOUTH, 10)

                        vbox_container.Add(vbox, 1, wx.EXPAND | wx.EAST | wx.WEST, 10)

                        close_btn = wx.Button(self, label='Close')
                        close_btn.Bind(wx.EVT_BUTTON, lambda event: self.Close(True))
                        vbox_container.Add(close_btn, 0, wx.ALIGN_RIGHT | wx.SOUTH | wx.EAST, 5)

                        self.SetSizer(vbox_container)
                        self.SetMinSize(wx.Size(400, 300))
                        self.SetSize(wx.Size(500, 500))
                        self.Center()

                EULADialog(self).ShowModal()

        about_dlg = AboutDialog(self, f'About {self.software_info.name}')
        about_dlg.ShowModal()

    def on_license_manager(_):
        """Creates license management dialog."""

        class LicenseManagerDialog(wx.Dialog):
            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, title='Aldras License Manager', name='license_manager_dialog')
                self.SetIcon(wx.Icon('data/aldras.ico', wx.BITMAP_TYPE_ICO))
                self.SetBackgroundColour('white')
                self.parent = parent
                panel = wx.Panel(self)

                self.margin_y = 10
                self.margin_x = 10

                self.vbox = wx.BoxSizer(
                    wx.VERTICAL)  # ------------------------------------------------------------------------

                self.hbox_logo_name_version = wx.BoxSizer(wx.HORIZONTAL)

                # add rescaled logo image
                png = wx.Image('data/aldras.png', wx.BITMAP_TYPE_PNG).Scale(60, 60, quality=wx.IMAGE_QUALITY_HIGH)
                self.logo_img = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(png))
                self.hbox_logo_name_version.Add(self.logo_img, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)
                self.vbox_name_version = wx.BoxSizer(wx.VERTICAL)

                # add program name text
                self.program_name = wx.StaticText(self, label=f'Aldras Automation')
                change_font(self.program_name, size=16, color=3 * (20,))
                self.vbox_name_version.Add(self.program_name, 0, wx.ALIGN_CENTER_HORIZONTAL)

                # add program version text
                self.program_version = wx.StaticText(self, label=f'Version 2021')
                change_font(self.program_version, size=10, style=wx.ITALIC, color=3 * (80,))
                self.vbox_name_version.Add(self.program_version, 0, wx.ALIGN_CENTER_HORIZONTAL)

                self.hbox_logo_name_version.Add(self.vbox_name_version, 0, wx.ALIGN_CENTER_VERTICAL)
                self.vbox.Add(self.hbox_logo_name_version, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EAST | wx.WEST, 30)

                self.vbox.AddSpacer(20)

                license_key_input = wx.TextCtrl(panel, wx.ID_ANY, value='Open-Source Version',
                                                size=(280, -1), style=wx.TE_READONLY | wx.TE_CENTRE)
                self.vbox.Add(license_key_input, 0, wx.ALIGN_CENTER_HORIZONTAL)  # | wx.EAST | wx.WEST, 30)
                self.vbox.AddSpacer(40)

                self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                self.vbox_outer.AddSpacer(self.margin_y)  # north margin
                self.vbox_outer.Add(self.vbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EAST | wx.WEST, self.margin_x)

                # display frame
                panel.SetSizerAndFit(self.vbox_outer)
                self.vbox_outer.SetSizeHints(self)
                # license_key_input.SetFocus()
                self.Center()
                self.Show()

            def pause_subscription(self, _):
                pass

        license_manager_dlg = LicenseManagerDialog(self)
        license_manager_dlg.ShowModal()

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
                    settings = import_settings()

                    self.padding = 5
                    self.margin = 40

                    self.menubar = wx.MenuBar()

                    self.freeze_menu = wx.Menu()
                    self.cb_click_freeze = self.freeze_menu.Append(wx.ID_ANY, 'Freeze when mouse clicked',
                                                                   kind=wx.ITEM_CHECK)
                    self.cb_ctrl_freeze = self.freeze_menu.Append(wx.ID_ANY, 'Freeze when CTRL tapped',
                                                                  kind=wx.ITEM_CHECK)

                    if 'click' in settings['Freeze method'].lower():
                        self.freeze_menu.Check(self.cb_click_freeze.GetId(), True)
                    if 'ctrl' in settings['Freeze method'].lower():
                        self.freeze_menu.Check(self.cb_ctrl_freeze.GetId(), True)

                    self.menubar.Append(self.freeze_menu, 'Freeze Actions')

                    def toggle_stay_on_top(event):
                        if event.IsChecked():
                            self.SetWindowStyleFlag(wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
                        else:
                            self.SetWindowStyleFlag(wx.DEFAULT_FRAME_STYLE)

                    # add view menu to allow toggle to stay on top
                    self.view_menu = wx.Menu()
                    self.stay_on_top = self.view_menu.Append(wx.ID_ANY, 'Always visible', kind=wx.ITEM_CHECK)
                    self.Bind(wx.EVT_MENU, lambda event: toggle_stay_on_top(event), self.stay_on_top)

                    self.menubar.Append(self.view_menu, 'View')

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
                    x_range, y_range, _ = get_system_parameters()
                    display_size = (x_range[1], y_range[1])  # kind of, only the maximum coordinates now but good enough
                    self.current_coords = wx.StaticText(self, label=f'{display_size}')
                    change_font(self.current_coords, size=22, color=3 * (60,))
                    self.vbox_live.Add(self.current_coords, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH, 4 * self.padding)

                    # add coordinate label
                    coords_label_spacer = ' ' * len(str(display_size))
                    x_coord_spacer = ' ' * int(len(str(x_range[1])) / 2)
                    y_coord_spacer = ' ' * int(len(str(y_range[1])) / 2)
                    self.coords_label = wx.StaticText(self,
                                                      label=f'{x_coord_spacer}x{coords_label_spacer}y{y_coord_spacer}')
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
                                output = f'({x}, {y})'  # the standard is that (0, 0) is upper left corner of the main displays with the x-coordinate increasing as the cursor moves right and the y-coordinate increasing as the cursor moves down. Note this is different from the standard cartesian coordinates in common mathematics. Aldras has chosen the less familiar established cursor coordinate system to allow users to apply workflow data generated in Aldras to other tools.

                                self.parent.current_coords.SetLabel(output)  # set current coordinates
                                if len(
                                        output) != self.prev_output_len:  # change 'x' and 'y' label spacing if length is different
                                    self.prev_output_len = len(output)

                                    coords_label_spacer = ' ' * len(output)
                                    x_coord_spacer = ' ' * int(len(str(x)) / 2)
                                    y_coord_spacer = ' ' * int(len(str(y)) / 2)
                                    self.parent.coords_label.SetLabel(
                                        f'{x_coord_spacer}x{coords_label_spacer}y{y_coord_spacer}')

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

                            self.key_listener = keyboard.Listener(on_press=on_key_press)
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

    def on_open(_):
        """ Open a file"""
        dlg = wx.FileDialog(self, 'Choose a file', wildcard='Aldras and text files (*.aldras;*.txt)|*.aldras;*.txt')
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            launch_workflow(self, os.path.join(dirname, filename))
            if self.Name == 'edit_frame':
                self.Destroy()
        dlg.Destroy()

    if status_bar:
        self.CreateStatusBar()

    # create menu bar
    menu_bar = wx.MenuBar()

    ############
    # set up the file menu
    file_menu = wx.Menu()

    menu_about = file_menu.Append(wx.ID_ABOUT, 'About', f'   Information about {self.software_info.name}')
    self.Bind(wx.EVT_MENU, on_about, menu_about)

    menu_new = file_menu.Append(wx.ID_ANY, 'New...\tCtrl+N', f'   Create new {self.software_info.name} workflow')
    self.Bind(wx.EVT_MENU, lambda event: self.close_window(), menu_new)  # go back to selection from edit frame
    if self.GetName() != 'edit_frame':
        menu_new.Enable(False)

    menu_open = file_menu.Append(wx.ID_ANY, 'Open...\tCtrl+O', f'   Open existing {self.software_info.name} workflow')
    self.Bind(wx.EVT_MENU, lambda event: on_open(event), menu_open)

    menu_save = file_menu.Append(wx.ID_ANY, 'Save\tCtrl+S', f'   Save {self.software_info.name} workflow')
    self.Bind(wx.EVT_MENU, lambda event: self.save_to_file(), menu_save)  # call EditFrame self.save_workflow()
    if self.GetName() != 'edit_frame':
        menu_save.Enable(False)

    # TODO enable 'Save As'
    # menu_save_as = file_menu.Append(wx.ID_ANY, 'Save as...', f'   Save {self.software_info.name} workflow as...')
    # # self.Bind(wx.EVT_MENU, ???, menu_save_as)
    # if self.GetName() != 'edit_frame':
    #     menu_save_as.Enable(False)

    menu_delete = file_menu.Append(wx.ID_ANY, 'Delete', f'   Delete {self.software_info.name} workflow')
    self.Bind(wx.EVT_MENU, lambda event: self.delete_workflow(), menu_delete)
    if self.GetName() != 'edit_frame':
        menu_delete.Enable(False)

    menu_refresh = file_menu.Append(wx.ID_ANY, 'Refresh', f'   Refresh {self.software_info.name} workflow editor')
    self.Bind(wx.EVT_MENU, lambda event: self.full_refresh(), menu_refresh)
    if self.GetName() != 'edit_frame':
        menu_refresh.Enable(False)

    menu_settings = file_menu.Append(wx.ID_ANY, 'Settings\tCtrl+,', f'   {self.software_info.name} settings')
    self.Bind(wx.EVT_MENU, lambda event: open_settings(self), menu_settings)

    menu_exit = file_menu.Append(wx.ID_EXIT, 'Exit', f'   Exit {self.software_info.name}')
    self.Bind(wx.EVT_MENU, on_exit, menu_exit)

    menu_bar.Append(file_menu, 'File')  # add the file menu to the menu bar

    ############
    # set up the tools menu
    tools_menu = wx.Menu()

    menu_mouse_monitor = tools_menu.Append(wx.ID_ANY, 'Mouse monitor\tCtrl+M',
                                           f'   {self.software_info.name} mouse monitoring tool')
    self.Bind(wx.EVT_MENU, on_mouse_monitor, menu_mouse_monitor)

    menu_license_manager = tools_menu.Append(wx.ID_ANY, 'License Manager',
                                             f'   {self.software_info.name} license manager tool')
    self.Bind(wx.EVT_MENU, on_license_manager, menu_license_manager)

    menu_bar.Append(tools_menu, 'Tools')  # add the insert menu to the menu bar

    ############
    # set up the insert menu
    if self.GetName() == 'edit_frame' and self.features_unlocked:
        self.variables_menu = wx.Menu()
        menu_bar.Append(self.variables_menu, 'Variables')  # add the insert menu to the menu bar

        self.internet_connection = self.variables_menu.Append(wx.ID_ANY, 'internet.conn',
                                                              '   Insert variable that outputs if connected to the internet (True or False).')
        self.Bind(wx.EVT_MENU, lambda event: self.insert_variable(event, self.internet_connection),
                  self.internet_connection)

        self.clipboard = self.variables_menu.Append(wx.ID_ANY, 'clipboard.value',
                                                    '   Insert variable that outputs the clipboard text content.')
        self.Bind(wx.EVT_MENU, lambda event: self.insert_variable(event, self.clipboard), self.clipboard)

        # disable all variable menu items for them to be re-enabled when focus is bestowed upon appropriate window
        for variable_menu_item in self.variables_menu.GetMenuItems():
            variable_menu_item.Enable(False)

    ############
    # set up the help menu
    help_menu = wx.Menu()

    menu_getting_started = help_menu.Append(wx.ID_ANY, 'Getting Started',
                                            f'   {self.software_info.name} getting started guide')
    self.Bind(wx.EVT_MENU, lambda event: webbrowser.open_new_tab('https://aldras.netlify.com/docs#quickstart'),
              menu_getting_started)

    menu_command_ref = help_menu.Append(wx.ID_ANY, 'Command Reference',
                                        f'   {self.software_info.name} command reference')
    self.Bind(wx.EVT_MENU, lambda event: webbrowser.open_new_tab('https://aldras.netlify.com/docs#commands'), menu_command_ref)
    # self.Bind(wx.EVT_MENU, lambda event: launch_edit_guide(self), menu_command_ref)

    menu_recording_tips = help_menu.Append(wx.ID_ANY, 'Recording', f'   {self.software_info.name} recording tips')
    self.Bind(wx.EVT_MENU, lambda event: webbrowser.open_new_tab('https://aldras.netlify.com/docs#recording'),
              menu_recording_tips)

    menu_execution_tips = help_menu.Append(wx.ID_ANY, 'Execution', f'   {self.software_info.name} execution tips')
    self.Bind(wx.EVT_MENU, lambda event: webbrowser.open_new_tab('https://aldras.netlify.com/docs#execution'),
              menu_execution_tips)

    menu_feedback = help_menu.Append(wx.ID_ANY, 'Submit Feedback',
                                     f'   Submit feedback to {self.software_info.name}')
    self.Bind(wx.EVT_MENU, lambda event: webbrowser.open_new_tab('https://aldras.netlify.com/contact'), menu_feedback)

    menu_bar.Append(help_menu, 'Help')  # add the insert menu to the menu bar

    ############
    # finalize setup
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


def launch_workflow(parent, workflow_path_name, recent_launch=False):
    if recent_launch:
        # when launching recent workflow, make sure it still exists and read lines
        try:
            with open(workflow_path_name, 'r') as record_file:
                pass
        except FileNotFoundError:
            wx.MessageDialog(parent,
                             f'The recent workflow at \'{workflow_path_name}\' no longer exists.\nIt may have been renamed, moved, or deleted.',
                             'Missing workflow', wx.OK | wx.ICON_WARNING).ShowModal()

            parent.recent_workflows = eliminate_duplicates(parent.recent_workflows)
            parent.recent_workflows.remove(workflow_path_name)
            parent.update_recent_workflows()
            return

    if parent.Name == 'selection_frame':
        selection_frame = parent
    elif parent.Name == 'edit_frame':
        selection_frame = parent.parent

    if workflow_path_name[-4:] == '.txt':
        selection_frame.workflow_name = ntpath.basename(workflow_path_name)[:-4]
    elif workflow_path_name[-7:] == '.aldras':
        selection_frame.workflow_name = ntpath.basename(workflow_path_name)[:-7]

    selection_frame.workflow_path_name = workflow_path_name

    # read or create workflow file
    try:
        with open(workflow_path_name, 'r') as record_file:
            if workflow_path_name[-4:] == '.txt':
                lines = record_file.readlines()

            elif workflow_path_name[-7:] == '.aldras':
                encrypted_lines = record_file.readlines()
                lines = []
                for line in encrypted_lines:
                    lines.append(fernet.decrypt(line.encode()).decode())

            else:
                print('INVALID WORKFLOW EXTENSION on ingest')

    except FileNotFoundError:  # create file if not found
        with open(workflow_path_name, 'w'):
            lines = []
    lines = [line.replace('\n', '') for line in lines]

    too_many_lines_thresh = parent.settings['Large lines number']
    if len(lines) > too_many_lines_thresh:
        confirm_long_workflow_dlg = wx.MessageDialog(None,
                                                     f'"{selection_frame.workflow_name}" has {len(lines)} lines.\n\nUsing loops and other tools is recommended to optimize workflows to less than {too_many_lines_thresh} lines to maximize the speed and stability of {selection_frame.software_info.name}.\n\nContinue anyway?',
                                                     'Long Workflow Warning',
                                                     wx.YES_NO | wx.ICON_WARNING | wx.CENTRE)

        if confirm_long_workflow_dlg.ShowModal() == wx.ID_NO:
            return

    selection_frame.Hide()
    EditFrame(selection_frame, lines)

    # add recently launched workflow to history
    selection_frame.recent_workflows.insert(0, selection_frame.workflow_path_name)

    # update frame
    selection_frame.update_recent_workflows()
    selection_frame.workflow_panel.SetSizerAndFit(selection_frame.vbox_outer)
    selection_frame.vbox_outer.SetSizeHints(selection_frame)
    selection_frame.Fit()


def launch_edit_guide(parent):
    global adv_edit_guide
    if not adv_edit_guide or not adv_edit_guide.IsShown():  # only if window does not yet exist or is not shown
        adv_edit_guide = AdvancedEditGuide(parent)
    else:
        adv_edit_guide.Raise()  # bring existing edit guide to top


class CustomGrid(wx.grid.Grid):
    def __init__(self, parent, table_size, style=wx.WANTS_CHARS, can_change_num_rows=True, can_change_num_cols=True,
                 formatting_function=None):
        wx.grid.Grid.__init__(self, parent, style=style)
        self.parent = parent
        self.CreateGrid(*table_size)
        self.editor = wx.grid.GridCellAutoWrapStringEditor()
        self.SetDefaultEditor(self.editor)
        self.SetDefaultRenderer(wx.grid.GridCellAutoWrapStringRenderer())

        self.can_change_num_rows = can_change_num_rows
        self.can_change_num_cols = can_change_num_cols

        self.formatting_function = formatting_function

        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, lambda
            event: self.resize_rows())  # when selected cell changes, autoresize the rows and layout the parent window
        self.Bind(wx.EVT_CHAR_HOOK, self.on_frame_char_hook)  # when key is pressed

    def resize_rows(self):
        self.AutoSizeRows()
        self.parent.GetParent().Layout()

    def on_frame_char_hook(self, event):
        """Process key presses"""

        if event.ControlDown() and (event.GetKeyCode() == wx.WXK_BACK or event.GetKeyCode() == wx.WXK_DELETE):
            self.clear_cells()

        elif event.ControlDown() and event.GetKeyCode() == 86:  # if CTRL+V
            self.paste_clipboard()

        elif event.ControlDown() and event.GetKeyCode() == 67:  # if CTRL+C
            # TODO process copy events
            pass

        elif event.ControlDown() and event.GetKeyCode() == 90:  # if CTRL+Z
            # TODO process undo events
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
        clipboard_text = pyperclip.paste()
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
        for row_index in range(row_selection, row_selection + excel_array.shape[0]):
            if row_index >= self.GetNumberRows():
                if not self.can_change_num_rows:
                    break  # stop if cannot change the number of rows
                else:
                    self.AppendRows()

            for column_index in range(col_selection, col_selection + excel_array.shape[1]):
                if column_index >= self.GetNumberCols():
                    if not self.can_change_num_cols:
                        break  # stop if cannot change the number of rows
                    else:
                        self.AppendCols()

                self.SetCellValue(row_index, column_index,
                                  excel_array[row_index - row_selection, column_index - col_selection])

        if self.formatting_function:
            self.formatting_function()

        self.resize_rows()


class AdvancedEditGuide(wx.Dialog):
    def __init__(self, parent):
        if parent.Name == 'selection_frame':
            self.software_info = parent.software_info
            self.workflow_name = ''
        else:
            self.software_info = parent.parent.software_info
            self.workflow_name = parent.parent.workflow_name
        wx.Dialog.__init__(self, parent, title=f'{self.software_info.name} Edit Guide',
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

        self.vbox_inner.AddSpacer(10)

        # add advanced edit guide description
        self.hbox_description = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_description.AddSpacer(5)
        self.description = wx.StaticText(self, label=self.software_info.advanced_edit_guide_description)
        self.hbox_description.Add(self.description)
        self.vbox_inner.Add(self.hbox_description)

        self.vbox_inner.AddSpacer(10)

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

        # add documentation description
        docs_description = wx.StaticText(self,
                                         label='For more including information about\nconditionals and loops...',
                                         style=wx.ALIGN_CENTRE_HORIZONTAL)
        change_font(docs_description, size=10, family=wx.DECORATIVE, color=3 * (100,))
        self.vbox_inner.Add(docs_description, 0, wx.CENTER | wx.SOUTH, 8)

        # add documentation title
        self.docs = wx.StaticText(self, label='Read the Docs')
        change_font(self.docs, size=13, family=wx.DECORATIVE, color=3 * (60,))
        config_status_and_tooltip(self, self.docs, tooltip='More Documentation')
        self.vbox_inner.Add(self.docs, 0, wx.CENTER)

        # TODO add documentation link
        self.docs_link = wx.adv.HyperlinkCtrl(self, wx.ID_ANY,
                                              label=f'{self.software_info.name.lower()}.com/docs',
                                              url=f'{self.software_info.website}/docs',
                                              style=wx.adv.HL_DEFAULT_STYLE)
        config_status_and_tooltip(self, self.docs_link, tooltip=f'{self.software_info.website}/docs')
        change_font(self.docs_link, size=11, family=wx.DECORATIVE)
        self.vbox_inner.Add(self.docs_link, 0, wx.CENTER)

        self.vbox_inner.AddSpacer(15)
        self.vbox_inner.AddStretchSpacer()

        self.hbox_outer.AddStretchSpacer()
        self.hbox_outer.Add(self.vbox_inner, 0, wx.CENTER | wx.EXPAND | wx.ALL, 10)
        self.hbox_outer.AddStretchSpacer()

        self.SetSizerAndFit(self.hbox_outer)
        self.hbox_outer.SetSizeHints(self)

        self.Center()
        self.Show()


class EditFrame(wx.Frame):
    """Frame to edit specific workflow."""

    def __init__(self, parent, lines, show_frame=True, previous_lines_when_launched=None):
        t0 = time.time()
        self.software_info = parent.software_info
        self.workflow_name = parent.workflow_name
        self.workflow_name_when_launched = parent.workflow_name
        self.parent = parent
        self.lines = lines
        self.license_type = parent.license_type
        self.features_unlocked = any(x in self.license_type for x in advanced_feature_license_types)
        self.internet_connection = None
        self.clipboard = None
        self.variables_menu_items = dict()
        self.variable_insertion_window = None
        self.variables_menu = None
        self.duplicate_variables = list()
        wx.Frame.__init__(self, parent, title=f'{self.software_info.name}: Edit - {self.workflow_name}',
                          name='edit_frame')
        setup_frame(self, status_bar=True)

        # set parameters
        self.settings = import_settings()
        self.margin = 10
        self.num_hotkeys = self.settings['Number of hotkeys']
        self.default_coords = (10, 10)
        self.loading_dlg_line_thresh = 25

        global hardware_id
        self.x_range, self.y_range, hardware_id = get_system_parameters()
        self.coord_width = 15 * max(
            [len(str(r)) for r in self.x_range + self.y_range])  # ten times the max length of range in x or y direction

        self.conditional_operations = ['Equals', 'Not equal to', 'Contains', 'Is in', '>', '<', '>=', '<=']
        self.loop_behaviors = ['Forever', 'Multiple times',
                               'For each element in list',
                               'For each row in table']  # TODO add later___, 'For each row in table', 'For each column in table']

        # read workflow hardware id
        self.workflow_hardware_id = None
        if self.lines:
            if 'hardware' in self.lines[0].strip().split(' ')[0].lower():  # if 'hardware' in first word of first line
                self.workflow_hardware_id = int(re.search(r'\d+', self.lines[0]).group())
                del self.lines[0]

        def create_bitmaps(source_file_name: str, size: tuple, default_contrast=100, flip=False, hover_red=False):
            # manipulate default image
            size = (int(size[0]), int(size[1]))  # convert to integers
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
        self.delete_x_bitmap, self.delete_x_bitmap_hover = create_bitmaps('delete_x', self.delete_x_size,
                                                                          hover_red=True)

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
        change_font(self.title, size=18, color=3 * (60,))
        self.title.Bind(wx.EVT_BUTTON, self.rename_workflow)
        self.title.Bind(wx.EVT_ENTER_WINDOW, lambda event: change_font(self.title, size=18, color=3 * (120,)))
        self.title.Bind(wx.EVT_LEAVE_WINDOW, lambda event: change_font(self.title, size=18, color=3 * (60,)))
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
        self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.add_command())
        config_status_and_tooltip(self, self.plus_btn, 'Add command', 'Add command')
        self.hbox_line_mods.Add(self.plus_btn, 1)

        self.vbox_action.Add(self.hbox_line_mods, 0, wx.EXPAND | wx.SOUTH, 5)

        # # add reorder commands button
        # self.reorder_btn = wx.Button(self, label='Reorder')
        # self.reorder_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_reorder_dialog())
        # config_status_and_tooltip(self, self.reorder_btn, 'Reorder commands', 'Reorder commands')
        # self.vbox_action.Add(self.reorder_btn, 0, wx.EXPAND | wx.SOUTH, 10)

        # add advanced command button
        if self.features_unlocked:
            self.advanced_btn = wx.Button(self, label='Advanced')
            self.advanced_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_advanced_edit_frame())
            config_status_and_tooltip(self, self.advanced_btn, 'Advanced text-based editor',
                                      'Advanced text-based editor')
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
        if show_frame:
            self.Show()

        self.lines_when_launched = self.lines.copy()

        # add command widgets
        self.edit.Freeze()
        self.render_lines()
        self.edit.Thaw()

        # used for comparison when closing
        if previous_lines_when_launched:
            self.lines_when_launched = previous_lines_when_launched

        print(f'Time to open entire Edit frame ({len(self.lines)}): {time.time() - t0:.2f} s')

        # compare system hardware id to workflow hardware id
        if hardware_id != self.workflow_hardware_id and self.lines:
            wx.MessageDialog(self,
                             'Your hardware configuration is different from the system that last made changes to this workflow.\n\nMouse coordinates and other features may not work as intended.',
                             'Different Hardware Configuration', wx.OK | wx.ICON_INFORMATION).ShowModal()

    def create_bitmap_btn(self, parent, size, bitmap, hover_keyword, description, tooltip='', focus_change=True):
        size = (int(size[0]), int(size[1]))  # convert to integers
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
        text_ctrl.Validator = CharValidator('file_name', self)  # assign validator for filename

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
        self.vbox_edit_container.SetMinSize(wx.Size(750, 300))
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

        # add missing ending brackets and remove extra ending brackets
        end_brackets_expected = 0
        extra_end_bracket_indices = []
        for index, line in enumerate(self.lines):
            line_first_word = line.strip().split(' ')[0].lower()[:6]
            if self.features_unlocked and (('if' in line_first_word and '{{~' in line and '~}}' in line) or (
                    'loop' in line_first_word and '{' in line)):
                # add ending bracket at end of workflow if block ending bracket cannot be found
                if block_end_index(self.lines, index) == -1:
                    self.lines.append('}')
                end_brackets_expected += 1

            elif line_first_word == '}' and end_brackets_expected:
                end_brackets_expected -= 1

            elif line_first_word == '}' and end_brackets_expected <= 0:
                extra_end_bracket_indices.append(index)

        # delete extra ending bracket lines (must be done in reverse order)
        for index in sorted(extra_end_bracket_indices, reverse=True):
            del self.lines[index]

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

        self.Freeze()
        for index, line_orig in enumerate(self.lines):
            self.create_command_sizer(index, line_orig)
            if len(self.lines) > self.loading_dlg_line_thresh:
                # update loading dialog and return to SelectionFrame if cancelled
                if not \
                        self.loading_dlg.Update(int(0.99 * (index + 1)),
                                                f'Loading line {index + 1} of {len(self.lines)}.')[0]:
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

        # all tracker lists must be modified when altering command order or adding/deleting
        self.tracker_lists = [self.lines, self.edit_row_container_sizers, self.edit_row_widget_sizers, self.indents]

        self.refresh_move_buttons()
        self.Layout()
        self.Thaw()

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
                if self.next_indent < 0 and self.features_unlocked:
                    print('Extra end bracket was rendered but should have been caught on ingest in render_lines().')
                    raise ValueError
                end_indent = True
            else:
                # add move buttons
                self.vbox_move = wx.BoxSizer(
                    wx.VERTICAL)  # ---------------------------------------------------------------

                self.move_up = self.create_bitmap_btn(self.edit, self.move_btn_size, self.up_arrow_bitmap, 'move_up',
                                                      'Move command up')
                self.move_up.Bind(wx.EVT_BUTTON,
                                  lambda event, sizer_trap=self.hbox_edit: self.move_command_up(sizer_trap))
                self.vbox_move.Add(self.move_up, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, 5)
                if index == 0:
                    self.move_up.Show(False)  # hide move up button if topmost command

                # add spacer to preserve width (mainly for when adding single command)
                self.vbox_move.Add(self.vbox_move.GetSize()[0], -1, 0)

                self.move_down = self.create_bitmap_btn(self.edit, self.move_btn_size, self.down_arrow_bitmap,
                                                        'move_down',
                                                        'Move command down')
                self.move_down.Bind(wx.EVT_BUTTON,
                                    lambda event, sizer_trap=self.hbox_edit: self.move_command_down(sizer_trap))
                self.vbox_move.Add(self.move_down, 0, wx.ALIGN_CENTER_HORIZONTAL)
                if index == len(self.lines) - 1:
                    self.move_down.Show(False)  # hide move down button if bottommost command

                self.hbox_edit.Add(self.vbox_move, 0, wx.ALIGN_CENTER_VERTICAL | wx.WEST | wx.EAST, 8)
                # ----------------------------------------------------------------------------------------------------------

                self.line_first_word = self.line.strip().split(' ')[0][:10]

                if not self.line:  # if line is empty, insert spacers
                    self.hbox_edit.Insert(2, 0, 30)

                elif self.line_first_word[0] == '#':  # workflow comment
                    self.add_command_combobox('Comment')
                    self.create_comment_row(line_orig)

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

                elif self.features_unlocked and ('assign' in self.line_first_word) and ('{{~' in self.line) and (
                        '~}}' in self.line):
                    if self.features_unlocked:
                        self.add_command_combobox('Assign')
                        self.create_assign_var_row(line_orig)
                    else:
                        self.add_command_combobox('Pro Command')

                elif 'if' in self.line_first_word and '{{~' in self.line and '~}}' in self.line:
                    if self.features_unlocked:
                        self.add_command_combobox('Conditional')
                        self.create_conditional_row(line_orig)
                    else:
                        self.add_command_combobox('Pro Command')

                elif ('loop' in self.line_first_word) and ('{' in self.line):
                    if self.features_unlocked:
                        self.add_command_combobox('Loop')
                        self.create_loop_sizer(line_orig)
                    else:
                        self.add_command_combobox('Pro Command')

                elif '-mouse' in self.line.strip().split(' ')[0]:
                    self.add_command_combobox('Mouse button')
                    self.create_mouse_row(self.line)

                elif 'pro command' in self.line:
                    self.add_command_combobox('Pro Command')

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
        self.indents.insert(index + 1, self.next_indent)

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
        config_status_and_tooltip(self, self.command, 'Command action')
        self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)
        self.hbox_edit.AddSpacer(10)

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
        mouse_button.Bind(wx.EVT_COMBOBOX, lambda event: self.command_parameter_change(sizer, event, 'mouse'))
        config_status_and_tooltip(self, mouse_button, 'Mouse button')

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
        mouse_action.Bind(wx.EVT_COMBOBOX, lambda event: self.command_parameter_change(sizer, event, 'mouse'))
        config_status_and_tooltip(self, mouse_action, 'Mouse action')

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

        def correct_coord_input(event):
            text_ctrl = event.GetEventObject()

            # set coord to integer of float found in input, eliminating leading zeros
            text_ctrl.SetValue(str(int(float_in(text_ctrl.GetValue()))))

            event.Skip()

        self.x_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE | wx.TE_RICH,
                                   size=wx.Size(self.coord_width, -1),
                                   value=str(x_val),
                                   validator=CharValidator('coordinate', self))
        self.x_coord.SetMaxLength(max([len(str(x)) for x in self.x_range]))
        self.x_coord.Bind(wx.EVT_TEXT, lambda event: self.command_parameter_change(sizer, event, 'coord_x'))
        self.x_coord.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        self.x_coord.Bind(wx.EVT_KILL_FOCUS, correct_coord_input)
        config_status_and_tooltip(self, self.x_coord, 'Mouse coordinate in the horizontal, x direction')

        self.y_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE | wx.TE_RICH,
                                   size=wx.Size(self.coord_width, -1),
                                   value=str(y_val),
                                   validator=CharValidator('coordinate', self))
        self.y_coord.SetMaxLength(max([len(str(y)) for y in self.y_range]))
        self.y_coord.Bind(wx.EVT_TEXT, lambda event: self.command_parameter_change(sizer, event, 'coord_y'))
        self.y_coord.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        self.y_coord.Bind(wx.EVT_KILL_FOCUS, correct_coord_input)
        config_status_and_tooltip(self, self.y_coord, 'Mouse coordinate in the vertical, y direction')

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

        text_value = str(line).replace('type:', '').replace('Type:', '').replace('``nl``', '\n')
        text_to_type = wx.lib.expando.ExpandoTextCtrl(self.edit, value=text_value)
        text_to_type.Bind(wx.EVT_TEXT, lambda event: self.command_parameter_change(sizer, event, 'type'))
        if self.features_unlocked:
            text_to_type.Bind(wx.EVT_SET_FOCUS, lambda event: self.enable_variable_insertion(True, sizer, event))
            text_to_type.Bind(wx.EVT_KILL_FOCUS, lambda event: self.enable_variable_insertion(False, sizer, event))
        config_status_and_tooltip(self, text_to_type, 'Text to type')
        sizer.Add(text_to_type, 1, wx.EXPAND)
        self.no_right_spacer = True

    def insert_variable(self, event, menu_item):
        if self.variable_insertion_window:
            insertion_text = f'{{{{~{menu_item.GetItemLabelText()}~}}}}'

            if self.variable_insertion_window.Name == 'variable_name_entry':
                insertion_text = menu_item.GetItemLabelText()
                self.variable_insertion_window.Clear()

            self.variable_insertion_window.WriteText(insertion_text)
        event.Skip()

    def enable_variable_insertion(self, enable_boolean, sizer, event):
        index = self.edit_row_widget_sizers.index(sizer)
        if enable_boolean:
            self.variable_insertion_window = event.GetEventObject()

            # enable built-in variables in variable insertion menu
            self.internet_connection.Enable(True)
            self.clipboard.Enable(True)

            # enable custom variables in variable insertion menu
            for line_index, line in enumerate(self.lines[:index]):
                line_first_word = line.strip().split(' ')[0][:6].lower()

                if 'assign' in line_first_word and '{{~' in line and '~}}' in line:
                    variable_name = variable_names_in(line)[0]
                    self.variables_menu_items[variable_name].Enable(True)

                if 'loop' in line_first_word and 'for each element in list' in line[:40].lower() and '{' in line:
                    loop_list_end_index = block_end_index(self.lines, line_index)
                    if index < loop_list_end_index:  # only enable loop.list.var insertion if line is before end of loop
                        self.variables_menu_items['loop.list.var'].Enable(True)

                if 'loop' in line_first_word and 'for each row in table' in line[:40].lower() and '{' in line:
                    loop_list_end_index = block_end_index(self.lines, line_index)
                    if index < loop_list_end_index:  # only enable loop.table variable insertion if line is before end of loop
                        _, table_vars = loop_table_data_from(line)
                        for table_var in table_vars:
                            self.variables_menu_items[f'loop.table.{table_var}'].Enable(True)

        else:
            self.variable_insertion_window = None

            # disable all variable menu items for them to be re-enabled when focus is bestowed upon appropriate window
            for variable_menu_item in self.variables_menu.GetMenuItems():
                variable_menu_item.Enable(False)

        event.Skip()

    def create_wait_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        value = '0'
        if not sizer:
            sizer = self.hbox_edit
            value = line.replace('wait', '').replace(' ', '')

        wait_entry = wx.TextCtrl(self.edit, value=value, style=wx.TE_RICH,
                                 validator=CharValidator('only_digit', self))
        wait_entry.Bind(wx.EVT_TEXT, lambda event: self.command_parameter_change(sizer, event, 'wait'))
        wait_entry.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        config_status_and_tooltip(self, wait_entry, 'Time to wait (seconds)')
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
        key.Bind(wx.EVT_COMBOBOX, lambda event: self.command_parameter_change(sizer, event, 'key'))
        key.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
        config_status_and_tooltip(self, key, 'Key')

        if 'tap' in line:
            action = 'Tap'
        elif 'press' in line:
            action = 'Press'
        elif 'release' in line:
            action = 'Release'
        else:
            raise ValueError
        key_action = wx.ComboBox(self.edit, value=action, choices=self.software_info.key_actions, style=wx.CB_READONLY)
        key_action.Bind(wx.EVT_COMBOBOX, lambda event: self.command_parameter_change(sizer, event, 'key_action'))
        key_action.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
        config_status_and_tooltip(self, key_action, 'Key action')

        sizer.Add(key, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(key_action, 0, wx.ALIGN_CENTER_VERTICAL)

    def create_hotkey_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        combination = [x.capitalize().replace(' ', '') for x in
                       line.replace('hotkey', '').split(' + ')]  # create list of keys
        combination += [''] * (
                self.num_hotkeys - len(combination))  # extend list with empty strings to reach standard number

        for index, key in enumerate(combination):
            hotkey_cb = wx.ComboBox(self.edit, value=str(key), choices=self.software_info.all_keys,
                                    style=wx.CB_READONLY)
            hotkey_cb.Bind(wx.EVT_COMBOBOX, lambda event: self.command_parameter_change(sizer, event, 'hotkey'))
            hotkey_cb.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
            config_status_and_tooltip(self, hotkey_cb, 'Hotkey')
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
        comment.Bind(wx.EVT_TEXT, lambda event: self.command_parameter_change(sizer, event, 'comment'))
        config_status_and_tooltip(self, comment, 'Comment')
        sizer.Add(comment, 2, wx.EXPAND)
        self.no_right_spacer = True

    def create_assign_var_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        variable_name_text = variable_names_in(line)[0]
        variable_name_entry = wx.TextCtrl(self.edit, value=variable_name_text, style=wx.TE_RICH | wx.TE_RIGHT,
                                          validator=CharValidator('variable_name', self))
        change_font(variable_name_entry, weight=wx.BOLD)
        variable_name_entry.SetMaxLength(15)
        variable_name_entry.Bind(wx.EVT_TEXT,
                                 lambda event: self.command_parameter_change(sizer, event, 'assign_var_name'))
        variable_name_entry.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        config_status_and_tooltip(self, variable_name_entry, 'Assignment variable name')
        sizer.Add(variable_name_entry, 0, wx.ALIGN_CENTER_VERTICAL)

        equals_text = non_flickering_static_text(self.edit, '  =  ')
        change_font(equals_text, size=14)
        sizer.Add(equals_text, 0, wx.ALIGN_CENTER_VERTICAL)

        variable_value_entry = wx.lib.expando.ExpandoTextCtrl(self.edit,
                                                              value=assignment_variable_value_in(line).replace('``nl``',
                                                                                                               '\n'))
        variable_value_entry.Bind(wx.EVT_TEXT,
                                  lambda event: self.command_parameter_change(sizer, event, 'assign_var_value'))
        variable_value_entry.Bind(wx.lib.expando.EVT_ETC_LAYOUT_NEEDED,
                                  lambda _: self.Layout())  # layout EditFrame when ExpandoTextCtrl size changes
        if self.features_unlocked:
            variable_value_entry.Bind(wx.EVT_SET_FOCUS,
                                      lambda event: self.enable_variable_insertion(True, sizer, event))
            variable_value_entry.Bind(wx.EVT_KILL_FOCUS,
                                      lambda event: self.enable_variable_insertion(False, sizer, event))
        config_status_and_tooltip(self, variable_value_entry, 'Assignment variable value')
        sizer.Add(variable_value_entry, 1, wx.ALIGN_CENTER_VERTICAL)
        self.no_right_spacer = True

        # add variable to menu
        if variable_name_text not in self.variables_menu_items:  # only add unique variable names on ingest
            # if the lowest variable menu item is a built-in variable (contains '.')
            if '.' in self.variables_menu.GetMenuItems()[-1].GetItemLabelText():
                self.variables_menu.AppendSeparator()  # add separator above custom variables

            self.variables_menu_items[variable_name_text] = self.variables_menu.Append(wx.ID_ANY, variable_name_text,
                                                                                       f'   Insert variable {variable_name_text}.')
            self.variables_menu_items[variable_name_text].Enable(
                False)  # to be re-enabled when focus is bestowed upon appropriate window
            self.Bind(wx.EVT_MENU,
                      lambda event: self.insert_variable(event, self.variables_menu_items[variable_name_text]),
                      self.variables_menu_items[variable_name_text])
        else:
            self.duplicate_variables.append(variable_name_text)

    def create_conditional_row(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        if_text = non_flickering_static_text(self.edit, 'If')
        change_font(if_text, size=11)
        sizer.Add(if_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 8)

        variable_name_entry = wx.TextCtrl(self.edit, value=variable_names_in(line)[0], style=wx.TE_RICH | wx.TE_RIGHT,
                                          validator=CharValidator('variable_name', self), name='variable_name_entry')
        change_font(variable_name_entry, weight=wx.BOLD)
        variable_name_entry.SetMaxLength(15)
        variable_name_entry.Bind(wx.EVT_TEXT,
                                 lambda event: self.command_parameter_change(sizer, event, 'conditional_var_name'))
        variable_name_entry.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        if self.features_unlocked:
            variable_name_entry.Bind(wx.EVT_SET_FOCUS, lambda event: self.enable_variable_insertion(True, sizer, event))
            variable_name_entry.Bind(wx.EVT_KILL_FOCUS,
                                     lambda event: self.enable_variable_insertion(False, sizer, event))
        config_status_and_tooltip(self, variable_name_entry, 'Conditional variable name')
        sizer.Add(variable_name_entry, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 5)

        comparator = wx.ComboBox(self.edit, value=conditional_operation_in(line, self.conditional_operations),
                                 choices=self.conditional_operations, style=wx.CB_READONLY)
        comparator.Bind(wx.EVT_TEXT,
                        lambda event: self.command_parameter_change(sizer, event, 'conditional_comparison_operator'))
        config_status_and_tooltip(self, comparator, 'Conditional comparator')

        comparator.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
        sizer.Add(comparator, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 5)

        comparison_entry = wx.lib.expando.ExpandoTextCtrl(self.edit,
                                                          value=conditional_comparison_in(line).replace('``nl``', '\n'))
        comparison_entry.Bind(wx.EVT_TEXT,
                              lambda event: self.command_parameter_change(sizer, event, 'conditional_comparison_value'))
        comparison_entry.Bind(wx.lib.expando.EVT_ETC_LAYOUT_NEEDED,
                              lambda _: self.Layout())  # layout EditFrame when ExpandoTextCtrl size changes
        if self.features_unlocked:
            comparison_entry.Bind(wx.EVT_SET_FOCUS, lambda event: self.enable_variable_insertion(True, sizer, event))
            comparison_entry.Bind(wx.EVT_KILL_FOCUS, lambda event: self.enable_variable_insertion(False, sizer, event))
        config_status_and_tooltip(self, comparison_entry, 'Conditional value')
        sizer.Add(comparison_entry, 1, wx.ALIGN_CENTER_VERTICAL)
        self.no_right_spacer = True
        self.next_indent += 1

    def create_loop_sizer(self, line, sizer=None):
        # sizer only passed to update, otherwise, function is called during initial panel creation
        if not sizer:
            sizer = self.hbox_edit

        try:
            behavior_value = [element for element in self.loop_behaviors if element.lower() in line.lower()][0]
        except IndexError:
            raise ValueError

        def add_loop_details(loop_sizer, action, modification):
            self.no_right_spacer = False

            index, old_loop_behavior = None, None
            if sizer in self.edit_row_widget_sizers:  # if changing loop_details, sizer will be in self.edit_row_widget_sizers
                index = self.edit_row_widget_sizers.index(sizer)
                old_loop_behavior = \
                    [element for element in self.loop_behaviors if element.lower() in self.lines[index].lower()][0]

            if modification:
                if old_loop_behavior == 'For each element in list':
                    self.remove_variable_menu_item('{{{{~loop.list.var~}}}}')

                elif old_loop_behavior == 'For each row in table':
                    _, table_vars = loop_table_data_from(self.lines[index])

                    # remove variables from menu
                    for table_var in table_vars:
                        self.remove_variable_menu_item(f'{{{{~loop.table.{table_var}~}}}}')

            for child in reversed(loop_sizer.GetChildren()):
                if child.GetWindow() == matching_widget_in_edit_row(loop_sizer, 'loop_behavior'):
                    break
                else:
                    child.Show(False)
                    loop_sizer.Remove(loop_sizer.GetChildren().index(child))

            if action == 'Forever':
                if index is not None:
                    self.lines[index] = 'Loop forever {'
            elif action == 'Multiple times':
                if index is not None:
                    self.lines[index] = 'Loop multiple times 1 {'
                    loop_num = '1'
                else:
                    loop_num = str(int(float_in(line)))
                loop_iteration_number = wx.TextCtrl(self.edit, value=loop_num, size=wx.Size(self.coord_width, -1),
                                                    style=wx.TE_RICH | wx.TE_CENTRE,
                                                    validator=CharValidator('only_integer', self))
                loop_iteration_number.SetMaxLength(4)
                loop_iteration_number.Bind(wx.EVT_TEXT, lambda event: self.command_parameter_change(sizer, event,
                                                                                                    'loop_multiple_times_number'))  # TODO add functionality
                loop_iteration_number.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
                config_status_and_tooltip(self, loop_iteration_number, 'Number of times to loop')
                loop_sizer.Add(loop_iteration_number, 0, wx.ALIGN_CENTER_VERTICAL)

            elif action == 'For each element in list':
                loop_line = line
                if index is not None:
                    self.lines[index] = "Loop for each element in list [1`'`2`'`3`'`4`'`5] {"
                    loop_line = self.lines[index]

                list_btn = wx.Button(self.edit, label='List')
                list_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_loop_list_grid(sizer))
                loop_sizer.Add(list_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)
                config_status_and_tooltip(self, list_btn, 'Loop list editor')

                loop_list_text = loop_line[loop_line.find('[') + 1:loop_line.rfind(
                    ']')]  # find text between first '[' and last ']'
                loop_list_values = loop_list_text.split("`'`")  # split based on delimiter
                loop_list_length = wx.StaticText(self.edit, label=f'{len(loop_list_values)} iterations',
                                                 name='loop_list_length')
                change_font(loop_list_length, style=wx.ITALIC, color=3 * (100,))
                loop_sizer.Add(loop_list_length, 0, wx.ALIGN_CENTER_VERTICAL)

                # add variable to menu
                if 'loop.list.var' not in self.variables_menu_items:  # only add unique variable names on ingest
                    self.variables_menu.InsertSeparator(2)
                    self.variables_menu_items['loop.list.var'] = self.variables_menu.Insert(3, wx.ID_ANY,
                                                                                            'loop.list.var',
                                                                                            '   Insert loop list variable created by the most recent loop list')
                    self.variables_menu_items['loop.list.var'].Enable(
                        False)  # to be re-enabled when focus is bestowed upon appropriate window
                    self.Bind(wx.EVT_MENU,
                              lambda event: self.insert_variable(event, self.variables_menu_items['loop.list.var']),
                              self.variables_menu_items['loop.list.var'])
                else:
                    self.duplicate_variables.append('loop.list.var')

            elif action == 'For each row in table':
                loop_line = line
                if index is not None:
                    self.lines[
                        index] = "Loop for each row in table [Name`'`ID`'`Country`'''`John Smith`'`1111`'`UK`'''`Amy Baker`'`2222`'`US] {"
                    loop_line = self.lines[index]

                table_btn = wx.Button(self.edit, label='Table')
                table_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_loop_table_grid(sizer))
                loop_sizer.Add(table_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)
                config_status_and_tooltip(self, table_btn, 'Loop table editor')

                loop_rows, table_vars = loop_table_data_from(loop_line)

                num_iterations = len(loop_rows) - 1
                num_iterations = 0 if num_iterations < 0 else num_iterations  # set negative values to zero (when header is deleted too)

                loop_table_length = wx.StaticText(self.edit, label=f'{num_iterations} iterations',
                                                  name='loop_table_length')
                change_font(loop_table_length, style=wx.ITALIC, color=3 * (100,))
                loop_sizer.Add(loop_table_length, 0, wx.ALIGN_CENTER_VERTICAL)

                self.update_loop_table_vars(table_vars, new_loop=True)

            loop_sizer.AddStretchSpacer()

            add_loop_commands_btn = wx.Button(self.edit, label='Add Commands')
            add_loop_commands_btn.Bind(wx.EVT_BUTTON, lambda event: self.open_add_loop_commands_dialog(sizer))
            loop_sizer.Add(add_loop_commands_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)
            config_status_and_tooltip(self, add_loop_commands_btn, 'Include commands to be looped')

            if modification:
                self.no_right_spacer = True
                self.create_delete_x_btn(loop_sizer)
                self.Layout()

        behavior_cb = wx.ComboBox(self.edit, value=behavior_value, choices=self.loop_behaviors, style=wx.CB_READONLY,
                                  name='loop_behavior')
        behavior_cb.Bind(wx.EVT_COMBOBOX,
                         lambda event, sizer_trap=sizer: add_loop_details(sizer_trap, event.GetString(),
                                                                          modification=True))
        behavior_cb.Bind(wx.EVT_MOUSEWHEEL, self.do_nothing)  # disable mouse wheel
        config_status_and_tooltip(self, behavior_cb, 'Loop behavior')
        sizer.Add(behavior_cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        add_loop_details(sizer, behavior_value, modification=False)

        self.no_right_spacer = True
        self.next_indent += 1

    def open_add_loop_commands_dialog(self, sizer):
        class AddLoopCommandsDialog(wx.Dialog):
            """Dialog to delete commands."""

            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
                self.SetIcon(wx.Icon(parent.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.SetTitle(f'Add Loop Commands - {parent.workflow_name}')
                self.SetBackgroundColour('white')

                sizer = wx.BoxSizer(wx.VERTICAL)

                sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Select the commands to add to the loop'), 0,
                          wx.ALL | wx.EXPAND, 10)

                self.check_list_box = wx.CheckListBox(self, wx.ID_ANY, choices=lines_not_in_loop, size=(300, -1),
                                                      style=wx.LB_HSCROLL)
                sizer.Add(self.check_list_box, 1, wx.ALL | wx.EXPAND, 10)

                # select all checkbox
                self.checkbox = wx.CheckBox(self, wx.ID_ANY, 'Select all')
                self.checkbox.Bind(wx.EVT_CHECKBOX, self.check_all)
                sizer.Add(self.checkbox, 0, wx.ALL | wx.EXPAND, 10)

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

        loop_start_index = self.edit_row_widget_sizers.index(sizer)
        loop_end_index = block_end_index(self.lines, loop_start_index)

        lines_before_loop = self.lines[:loop_start_index]
        lines_after_loop = self.lines[loop_end_index + 1:]

        if lines_before_loop or lines_after_loop:
            loop_separation_spaces = loop_end_index - loop_start_index + 1
            lines_not_in_loop = lines_before_loop + loop_separation_spaces * [''] + lines_after_loop
        else:
            wx.MessageDialog(self, 'There are no commands outside the loop.', 'No commands outside loop',
                             wx.OK | wx.ICON_INFORMATION).ShowModal()
            return

        add_loop_commands_dlg = AddLoopCommandsDialog(self)
        add_loop_commands_dlg.SetIcon(wx.Icon(self.software_info.icon, wx.BITMAP_TYPE_ICO))

        # center dialog
        add_loop_commands_dlg.Position = (int(self.Position[0] + ((self.Size[0] - add_loop_commands_dlg.Size[0]) / 2)),
                                          int(self.Position[1] + ((self.Size[1] - add_loop_commands_dlg.Size[1]) / 2)))
        add_loop_commands_dlg.SetBackgroundColour('white')

        if add_loop_commands_dlg.ShowModal() == wx.ID_OK:
            self.save_to_file()

            selections = add_loop_commands_dlg.get_selections()

            old_lines = self.lines.copy()

            new_lines = []

            for old_line_index, old_line in enumerate(old_lines):
                if old_line_index < loop_start_index and old_line_index not in selections:
                    new_lines.append(old_line)

                elif old_line_index == loop_start_index:  # start of index
                    new_lines.append(old_line)  # add loop statement

                    for selection_index in selections:  # add selected commands that were above loop command
                        if selection_index < loop_start_index:
                            new_lines.append(old_lines[selection_index])

                elif loop_start_index < old_line_index < loop_end_index:  # lines in old loop
                    new_lines.append(old_line)

                elif old_line_index == loop_end_index:  # end of index
                    for selection_index in selections:  # add selected commands that were below loop command
                        if selection_index > loop_end_index:
                            new_lines.append(old_lines[selection_index])

                    new_lines.append(old_line)  # add loop end statement

                elif old_line_index > loop_end_index and old_line_index not in selections:
                    new_lines.append(old_line)

            self.lines = new_lines

            self.full_refresh()

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
                    # cannot only delete ending bracket, must delete entire block or move ending bracket down
                    if self.lines[index].strip() != '}':
                        self.delete_command(index)
                self.Layout()

    def add_command(self):
        self.default_new_command = f'Left-mouse click at {self.default_coords}'
        self.lines.append(self.default_new_command)
        new_line_index = len(self.lines) - 1

        self.Freeze()

        self.create_command_sizer(new_line_index, self.lines[-1])

        # show move-down button of previously bottom-most command
        try:
            self.show_move_button(self.edit_row_container_sizers[-2], 'down', True)
        except IndexError:
            pass

        self.refresh_move_buttons()
        self.Layout()
        self.edit.ScrollChildIntoView([child.GetWindow() for child in list(self.hbox_edit.GetChildren()) if
                                       isinstance(child.GetWindow(), wx.ComboBox)][-1])
        self.Layout()
        self.Thaw()

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
        reorder_dlg.Position = (int(self.Position[0] + ((self.Size[0] - reorder_dlg.Size[0]) / 2)),
                                int(self.Position[1] + ((self.Size[1] - reorder_dlg.Size[1]) / 2)))
        reorder_dlg.SetBackgroundColour('white')

        if reorder_dlg.ShowModal() == wx.ID_OK:
            order = reorder_dlg.GetOrder()
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
                launch_edit_guide(self)

            def close_window(self, close_event):
                if adv_edit_guide:
                    adv_edit_guide.Close(True)
                close_event.Skip()

        adv_edit_dlg = AdvancedEdit(self)
        if adv_edit_dlg.ShowModal() == wx.ID_OK:
            if adv_edit_dlg.text_edit.GetValue().split('\n') != self.lines:
                # TODO find way to only add changes rather than compute entire panel again
                self.lines = adv_edit_dlg.text_edit.GetValue().split('\n')
                self.create_edit_panel()
                self.Layout()

    def open_loop_list_grid(self, sizer):

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

                if len(list_values) > 40:
                    num_elements = (len(list_values) + 9) // 10 * 10  # round number of elements up to nearest 10
                    self.grid = CustomGrid(self, table_size=(num_elements, 1), can_change_num_cols=False)
                else:
                    self.grid = CustomGrid(self, table_size=(40, 1), can_change_num_cols=False)

                self.grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
                self.grid.DisableColResize(0)
                self.grid.SetColLabelSize(1)  # hide column labels

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
                self.SetMinSize(wx.Size(vbox_container.GetSize()[0] + 120, wx.GetDisplaySize()[1] / 2))
                self.SetSize(self.GetMinSize())
                self.Center()
                self.Bind(wx.EVT_SIZE, self.resize_window)

                # set offset to autosize list column
                self.list_column_width_offset = self.vbox_action.GetMinSize()[
                                                    0] + self.grid.GetRowLabelSize() + 2 * margins + spacing_between_fg_sizers + 34

            def resize_window(self, event):
                """On window resize, resize column of list grid as well"""
                event.Skip()
                self.grid.SetColSize(0, self.GetSize()[0] - self.list_column_width_offset)
                self.grid.resize_rows()
                self.Refresh()

        index = self.edit_row_widget_sizers.index(sizer)
        line = self.lines[index]
        loop_list_text = line[line.find('[') + 1:line.rfind(']')]  # find text between first '[' and last ']'
        loop_list_values = loop_list_text.split("`'`")  # split based on delimiter

        loop_list_dlg = LoopListGrid(self, loop_list_values)
        loop_list_dlg.ShowModal()

        # get loop_list values by iterating through rows
        loop_list_values = [loop_list_dlg.grid.GetCellValue(row_index, 0) for row_index in
                            range(loop_list_dlg.grid.GetNumberRows())]

        loop_list_dlg.Destroy()

        # remove trailing empty list elements
        while loop_list_values and loop_list_values[-1] == '':
            loop_list_values.pop()  # remove last element

        loop_list_string = "`'`".join(loop_list_values)
        self.lines[index] = f'Loop for each element in list [{loop_list_string}] {{'

        matching_widget_in_edit_row(sizer, 'loop_list_length').SetLabel(f'{len(loop_list_values)} iterations')

    def open_loop_table_grid(self, sizer):

        class LoopTableGrid(wx.Dialog):
            """Dialog to edit loop list elements"""

            def __init__(self, parent, table_array):
                wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
                self.SetIcon(wx.Icon(parent.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.SetTitle(f'Loop Table: - {parent.workflow_name}')
                self.SetBackgroundColour('white')

                spacing_between_fg_sizers = 10
                fg_sizer = wx.FlexGridSizer(1, 2, spacing_between_fg_sizers, spacing_between_fg_sizers)

                # create sizer for grid
                self.vbox_table = wx.BoxSizer(wx.VERTICAL)

                num_rows = np.shape(table_array)[0]
                num_cols = np.shape(table_array)[1]

                if num_rows > 41:
                    num_rows_to_generate = (
                                                   num_rows + 9) // 10 * 10 + 1  # round number of elements up to nearest 10 (+1 for header row)
                    self.grid = CustomGrid(self, table_size=(num_rows_to_generate, num_cols), can_change_num_cols=True,
                                           formatting_function=self.format_grid)
                else:
                    self.grid = CustomGrid(self, table_size=(41, num_cols), can_change_num_cols=True,
                                           formatting_function=self.format_grid)

                self.grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
                self.grid.SetColLabelSize(2)  # hide column labels

                # set grid cell values
                for row_index, row in enumerate(table_array):
                    for col_index, element in enumerate(row):
                        self.grid.SetCellValue(row_index, col_index, element)

                self.format_grid()

                self.vbox_table.Add(self.grid, 1, wx.EXPAND)

                # add action widgets
                self.vbox_action = wx.BoxSizer(wx.VERTICAL)

                import_btn = wx.Button(self, label='Import Sheet')
                import_btn.Bind(wx.EVT_BUTTON, self.import_sheet)
                self.vbox_action.Add(import_btn, 0, wx.EXPAND | wx.SOUTH, 5)

                # import_btn = wx.Button(self, label='Paste Sheet')
                # import_btn.Bind(wx.EVT_BUTTON, self.paste_sheet)
                # self.vbox_action.Add(import_btn, 0, wx.EXPAND)

                self.vbox_action.AddStretchSpacer()

                clear_btn = wx.Button(self, label='Clear Cell')
                clear_btn.Bind(wx.EVT_BUTTON, lambda event: self.grid.clear_cells())
                self.vbox_action.Add(clear_btn, 0, wx.EXPAND | wx.SOUTH, 5)

                clear_all_btn = wx.Button(self, label='Clear All')
                clear_all_btn.Bind(wx.EVT_BUTTON, lambda event: self.grid.clear_all_cells())
                self.vbox_action.Add(clear_all_btn, 0, wx.EXPAND)

                self.vbox_action.AddStretchSpacer()

                add_rows_btn = wx.Button(self, label='Add Rows')
                add_rows_btn.Bind(wx.EVT_BUTTON, self.add_rows)
                self.vbox_action.Add(add_rows_btn, 0, wx.EXPAND | wx.SOUTH, 5)

                del_row_btn = wx.Button(self, label='Delete Row')
                del_row_btn.Bind(wx.EVT_BUTTON, self.del_row)
                self.vbox_action.Add(del_row_btn, 0, wx.EXPAND)

                self.vbox_action.AddStretchSpacer()

                add_col_btn = wx.Button(self, label='Add Column')
                add_col_btn.Bind(wx.EVT_BUTTON, self.add_col)
                self.vbox_action.Add(add_col_btn, 0, wx.EXPAND | wx.SOUTH, 5)

                del_col_btn = wx.Button(self, label='Delete Column')
                del_col_btn.Bind(wx.EVT_BUTTON, self.del_col)
                self.vbox_action.Add(del_col_btn, 0, wx.EXPAND)

                self.vbox_action.AddStretchSpacer()

                ok_btn = wx.Button(self, wx.ID_OK, label='OK')
                self.vbox_action.Add(ok_btn, 0, wx.EXPAND)

                fg_sizer.AddMany([(self.vbox_table, 1, wx.EXPAND), (self.vbox_action, 1, wx.EXPAND)])
                fg_sizer.AddGrowableCol(0, 0)
                fg_sizer.AddGrowableRow(0, 0)

                margins = 10
                vbox_container = wx.BoxSizer(wx.HORIZONTAL)
                vbox_container.Add(fg_sizer, 1, wx.EXPAND | wx.ALL, margins)

                self.SetSizer(vbox_container)
                vbox_container.SetSizeHints(self)
                self.SetMinSize(wx.Size(vbox_container.GetSize()[0] + 120, wx.GetDisplaySize()[1] / 2))
                self.SetSize(self.GetMinSize())
                self.Center()
                self.Bind(wx.EVT_SIZE, self.resize_window)

            def import_sheet(self, _):
                file_dlg = wx.FileDialog(self, 'Choose a file',
                                         wildcard='Excel and CSV files (*.xlsx;*.xls;*.csv)|*.xlsx;*.xls;*.csv')
                if file_dlg.ShowModal() == wx.ID_OK:
                    filename = file_dlg.GetFilename()
                    dirname = file_dlg.GetDirectory()
                    _, file_extension = os.path.splitext(filename)
                    complete_path = os.path.join(dirname, filename)

                    if file_extension in ['.xlsx', '.xls']:
                        df = pd.read_excel(complete_path, header=None, sheet_name=0)
                    elif file_extension == '.csv':
                        df = pd.read_csv(complete_path, header=None)
                    else:
                        file_dlg.Destroy()
                        return

                    self.grid.clear_all_cells()

                    # add any missing rows or columns
                    while self.grid.GetNumberRows() < df.shape[0] + 10:
                        self.grid.AppendRows(1)
                    while self.grid.GetNumberCols() < df.shape[1]:
                        self.grid.AppendCols(1)

                    self.format_grid()

                    for row_index, row in df.iterrows():
                        for col_index, element in row.iteritems():
                            element = '' if pd.isnull(element) else str(
                                element)  # set NaN or null elements equal to empty strings
                            self.grid.SetCellValue(row_index, col_index, element)

                    self.grid.resize_rows()

                file_dlg.Destroy()

            def paste_sheet(self, _):
                self.grid.clear_all_cells()
                self.grid.SetGridCursor(0, 0)
                self.grid.paste_clipboard()
                self.format_grid()

            def add_rows(self, _):
                self.grid.AppendRows(10)
                self.format_grid()

            def add_col(self, _):
                self.grid.AppendCols(1)
                self.format_grid()

            def del_row(self, _):
                row_index = self.grid.GetGridCursorRow()
                if self.grid.GetNumberRows() > 2 and row_index > 0:
                    self.grid.DeleteRows(row_index)

            def del_col(self, _):
                if self.grid.GetNumberCols() > 1:
                    self.grid.DeleteCols(self.grid.GetGridCursorCol())

            def format_grid(self):
                # format header row
                for col_index in range(self.grid.GetNumberCols()):
                    self.grid.SetCellBackgroundColour(0, col_index, wx.Colour(3 * (230,)))
                    self.grid.SetCellFont(0, col_index, wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD))

                # set row labels to account for header row
                self.grid.SetRowLabelValue(0, '')  # set blank for header row
                for row_index in range(1, self.grid.GetNumberRows()):
                    self.grid.SetRowLabelValue(row_index, str(row_index))

            def resize_window(self, event):
                """On window resize, resize column of list grid as well"""
                event.Skip()
                self.grid.resize_rows()
                self.Refresh()

        index = self.edit_row_widget_sizers.index(sizer)
        line = self.lines[index]
        loop_rows, _ = loop_table_data_from(line)
        loop_table_array = np.array([loop_row.split("`'`") for loop_row in loop_rows])  # split based on delimiter

        # remove current table headers from variable menu to be added back later
        table_vars = loop_rows[0].split("`'`")
        for table_var in table_vars:
            if table_var:
                self.remove_variable_menu_item(f'{{{{~loop.table.{table_var}~}}}}')

        loop_table_dlg = LoopTableGrid(self, loop_table_array)
        loop_table_dlg.ShowModal()

        # get loop table values
        table_array = []
        for row_index in range(loop_table_dlg.grid.GetNumberRows()):
            row_list = []
            for col_index in range(loop_table_dlg.grid.GetNumberCols()):
                row_list.append(loop_table_dlg.grid.GetCellValue(row_index, col_index))
            table_array.append(row_list)

        loop_table_dlg.Destroy()

        # remove trailing empty rows
        while table_array and not any([item for item in table_array[-1]]):
            table_array.pop()  # remove last element

        row_strings = ["`'`".join(row) for row in table_array]
        table_string = "`'''`".join(row_strings)

        self.lines[index] = f'Loop for each row in table [{table_string}] {{'

        num_iterations = len(table_array) - 1
        num_iterations = 0 if num_iterations < 0 else num_iterations  # set negative values to zero (when header is deleted too)

        matching_widget_in_edit_row(sizer, 'loop_table_length').SetLabel(f'{num_iterations} iterations')

        if table_array:
            self.update_loop_table_vars(table_array[0], new_loop=False)

    def update_loop_table_vars(self, header_elements, new_loop):
        table_vars = [f'loop.table.{var}' for var in header_elements if var]  # add 'loop.table.' to nonempty headers

        # add variables to menu
        for table_var in table_vars:
            if table_var not in self.variables_menu_items:  # only add unique variable names on ingest
                self.variables_menu_items[table_var] = self.variables_menu.Append(wx.ID_ANY, table_var,
                                                                                  '   Insert loop table variable created by the most recent loop table')
                self.variables_menu_items[table_var].Enable(
                    False)  # to be re-enabled when focus is bestowed upon appropriate window
                self.Bind(wx.EVT_MENU, lambda event, var_trap=table_var: self.insert_variable(event,
                                                                                              self.variables_menu_items[
                                                                                                  var_trap]),
                          self.variables_menu_items[table_var])
            else:
                if new_loop:
                    self.duplicate_variables.append(table_var)

    def delete_command(self, sizer_or_index):
        index = sizer_or_index  # this is the case when called from delete dialog
        if isinstance(sizer_or_index, wx.Sizer):
            index = self.edit_row_widget_sizers.index(sizer_or_index)

        line = self.lines[index]
        line_first_word = line.strip().split(' ')[0][:6].lower()
        self.Freeze()

        # if deleting indent block, decrease indents and delete ending bracket
        if self.features_unlocked:
            if ('if' in line_first_word and '{{~' in line and '~}}' in line) or (
                    'loop' in line_first_word and '{' in line):
                # find index of last element of indented block
                next_same_indent_offset = self.indents[index + 1:].index(
                    self.indents[index])  # distance between indent start and end
                end_bracket_indent = index + next_same_indent_offset

                for indent_index in range(index, end_bracket_indent + 1):  # decrease indent of entire indent block
                    self.indents[indent_index] -= 1

                for indent_index in range(index, end_bracket_indent + 1):  # reset indents of indent block
                    self.set_indent(indent_index)

                # only delete index of less indent if it is an end bracket
                # only not called from delete dialog where end bracket is deleted before beginning of indent block
                if self.lines[end_bracket_indent].strip() == '}':
                    for list_to_change in self.tracker_lists:  # delete end bracket from tracker_lists
                        del (list_to_change[end_bracket_indent])

                    self.vbox_edit.Show(end_bracket_indent, False)
                    self.vbox_edit.Remove(end_bracket_indent)

            if 'assign' in line_first_word and '{{~' in line and '~}}' in line:
                self.remove_variable_menu_item(line)

            if 'loop' in line_first_word and 'for each element in list' in line[:40].lower() and '{' in line:
                self.remove_variable_menu_item('{{{{~loop.list.var~}}}}')

            if 'loop' in line_first_word and 'for each row in table' in line[:40].lower() and '{' in line:
                _, table_vars = loop_table_data_from(line)
                # remove variables from menu
                for table_var in table_vars:
                    self.remove_variable_menu_item(f'{{{{~loop.table.{table_var}~}}}}')

        for list_to_change in self.tracker_lists:  # delete command from tracker_lists
            del (list_to_change[index])

        self.refresh_move_buttons()
        self.vbox_edit.Show(index, False)
        self.vbox_edit.Remove(index)
        self.Layout()
        self.Thaw()

    def remove_variable_menu_item(self, line):
        variable_name = variable_names_in(line)[0]

        if variable_name in self.duplicate_variables:
            self.duplicate_variables.remove(
                variable_name)  # remove variable from duplicate record if present in case future variable attempts to use the same name

        else:
            # try:
            self.variables_menu.DestroyItem(self.variables_menu_items[variable_name])  # destroy menu item
            self.variables_menu_items.pop(variable_name)  # remove variable from menu items record

        # destroy separator if there are not custom variables
        if self.variables_menu.GetMenuItems()[-1].GetKind() == wx.ITEM_SEPARATOR:
            self.variables_menu.DestroyItem(self.variables_menu.GetMenuItems()[-1])

        # remove extra separator when removing loop.list.var.
        if self.variables_menu.GetMenuItemCount() > 3:
            if self.variables_menu.GetMenuItems()[3].GetKind() == wx.ITEM_SEPARATOR:
                self.variables_menu.DestroyItem(self.variables_menu.GetMenuItems()[3])

    def move_command_up(self, sizer):
        index = self.edit_row_widget_sizers.index(sizer)

        if index > 0:  # cannot move up top-most command
            row_sizer = self.edit_row_container_sizers[index].GetChildren()[0].GetSizer()
            try:
                command_value = matching_widget_in_edit_row(row_sizer, 'command').GetStringSelection()
            except AttributeError:  # unknown command row (no command combobox)
                command_value = ''
            insertion_index = index  # location at which line that is 'in the way' will be inserted

            self.edit.Freeze()

            if command_value in ['Conditional', 'Loop']:  # move entire indented block

                # find index of last element of indented block
                next_same_indent_offset = self.indents[index + 1:].index(
                    self.indents[index])  # distance between indent start and end
                insertion_index = index + next_same_indent_offset  # index of end bracket, insertion occurs before this value

                if self.indents[index] > self.indents[index - 1]:  # if moving out of surrounding indent block
                    for ii in range(index, insertion_index + 1):
                        self.indents[ii] -= 1  # decrease indent of entire indent block
                elif self.indents[index] < self.indents[index - 1]:  # if moving into surrounding indent block
                    for ii in range(index, insertion_index + 1):
                        self.indents[ii] += 1  # increase indent of entire indent block
                for indent_index in range(index, insertion_index):
                    self.set_indent(indent_index)  # reset indents of indent block

            else:  # move single command row
                if self.indents[index] != self.indents[index - 1]:
                    self.indents[index] = self.indents[index - 1]  # set indent to preceding
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
                next_same_indent_offset = self.indents[index + 1:].index(
                    self.indents[index])  # distance between indent start and end
                detachment_index = index + next_same_indent_offset  # index of end bracket, detachment occurs at this value

                if self.indents[index] > self.indents[
                    detachment_index + 2]:  # if moving out of surrounding indent block

                    for ii in range(index, detachment_index + 1):
                        self.indents[ii] -= 1  # decrease indent of entire indent block

                elif self.indents[index] < self.indents[
                    detachment_index + 2]:  # if moving into surrounding indent block

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
        matching_widget_in_edit_row(self.edit_row_widget_sizers[indent_index], 'indent_text').SetLabel(
            self.indents[indent_index] * 20 * ' ')
        self.Layout()

    def refresh_move_buttons(self):
        for sizer_index, sizer_indiv in enumerate(self.edit_row_container_sizers):
            if len(self.edit_row_container_sizers) == 1:  # only one command
                self.show_move_button(sizer_indiv, 'up', False)
                self.show_move_button(sizer_indiv, 'down', False)

            elif sizer_index == 0:  # top-most command
                self.show_move_button(sizer_indiv, 'up', False)
                self.show_move_button(sizer_indiv, 'down', True)

            elif sizer_index == len(self.lines) - 1:  # bottom-most command
                self.show_move_button(sizer_indiv, 'up', True)
                self.show_move_button(sizer_indiv, 'down', False)

            else:
                self.show_move_button(sizer_indiv, 'up', True)
                self.show_move_button(sizer_indiv, 'down', True)

        # hide move down button of indent block start if nothing below indent block
        if self.indents[-2:] != [0, 0] and len(self.indents) >= 2:
            indent_block_start_index = len(self.indents[:-2]) - 1 - self.indents[:-2][::-1].index(
                0)  # index of last zero before indent block
            self.show_move_button(self.edit_row_container_sizers[indent_block_start_index], 'down', False)

        self.Layout()

    def command_combobox_change(self, sizer, event):
        self.Freeze()
        index = self.edit_row_widget_sizers.index(sizer)
        new_action = event.GetString()
        line_orig = self.lines[index]
        line = line_orig.lower().strip()
        line_first_word = line.split(' ')[0][:15]

        old_coords = self.default_coords
        old_action = ''
        if line.replace(' ', '')[0] == '#':
            old_action = 'Comment'

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

        elif 'if' in line_first_word and '{{~' in line and '~}}' in line:
            old_action = 'Conditional'

        elif 'loop' in line_first_word and '{' in line:
            old_action = 'Loop'

            old_loop_behavior = \
                [element for element in self.loop_behaviors if element.lower() in self.lines[index].lower()][0]

            if old_loop_behavior == 'For each element in list':
                self.remove_variable_menu_item('{{{{~loop.list.var~}}}}')

            elif old_loop_behavior == 'For each row in table':
                _, table_vars = loop_table_data_from(self.lines[index])

                # remove variables from menu
                for table_var in table_vars:
                    self.remove_variable_menu_item(f'{{{{~loop.table.{table_var}~}}}}')

        elif '-mouse' in line.split(' ')[0]:
            old_action = 'Mouse button'
            old_coords = coords_of(line)

        if old_action == new_action:  # do nothing as not to reset existing parameters
            self.Thaw()
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
            self.lines[index] = f'#{self.lines[index]}'
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
            self.create_assign_var_row(self.lines[index], sizer)

        elif new_action == 'Conditional':
            self.lines[index] = 'If {{~Var~}} equals ~value~ {'
            self.create_conditional_row(self.lines[index], sizer)
            self.indents[index + 1] += 1

            # add end of indent block
            self.lines.insert(index + 1, '}')
            self.create_command_sizer(index + 1, self.lines[index + 1])
            self.vbox_edit.Layout()

        elif new_action == 'Loop':
            self.lines[index] = 'Loop multiple times 5 {'
            self.create_loop_sizer(self.lines[index], sizer)
            self.indents[index + 1] += 1

            # add end of indent block
            self.lines.insert(index + 1, '}')
            self.create_command_sizer(index + 1, self.lines[index + 1])
            self.vbox_edit.Layout()

            self.no_right_spacer = True

        elif new_action == 'Pro Command':
            self.lines[index] = 'Pro Command'
            self.vbox_edit.Layout()

        self.create_delete_x_btn(sizer)

        if old_action in ['Conditional', 'Loop']:
            # delete end bracket for associated block
            index_of_end_bracket = index + [line.strip() for line in self.lines[index:]].index(
                '}')  # index of start in list plus index of end in sublist
            self.delete_command(self.edit_row_widget_sizers[index_of_end_bracket])

            # decrease indents for associated block
            for indent_index in range(index + 1, index_of_end_bracket):
                self.indents[indent_index] -= 1
                self.set_indent(indent_index)

            self.refresh_move_buttons()

        elif old_action == 'Assign':
            self.remove_variable_menu_item(line_orig)

        self.Layout()
        self.Thaw()

    def command_parameter_change(self, sizer, event, command_type):
        index = self.edit_row_widget_sizers.index(sizer)
        input_one_lined = event.GetString().replace('\n', '``nl``')
        if command_type == 'mouse':
            index = self.edit_row_widget_sizers.index(sizer)
            command_change = event.GetString()  # can be mouse_button change or mouse_action change

            # replace left or right
            if command_change in self.software_info.mouse_buttons:
                for replace_word in [x for x in self.software_info.mouse_buttons if
                                     x != command_change]:  # loop through remaining actions
                    self.lines[index] = re.compile(re.escape(replace_word), re.IGNORECASE).sub(command_change,
                                                                                               self.lines[
                                                                                                   index]).capitalize()

            # replace click, press, or release
            elif command_change in self.software_info.mouse_actions:
                for replace_word in [x for x in self.software_info.mouse_actions if
                                     x != command_change]:  # loop through remaining actions
                    self.lines[index] = re.compile(re.escape(replace_word), re.IGNORECASE).sub(command_change,
                                                                                               self.lines[
                                                                                                   index]).capitalize()

        elif 'coord' in command_type:
            command_change = event.GetString()  # will be empty if not input and should be converted to zero
            text_ctrl = event.GetEventObject()
            text_ctrl.SetForegroundColour(wx.BLACK)
            # find desired element by looping through all sizer children and filtering children with None windows and then the window with desired name
            error_static_text = matching_widget_in_edit_row(sizer, 'error_display')
            error_static_text.SetLabel('')

            # validate input and display feedback
            invalid_range = False
            try:
                # if key != '-' and not command_change.isdecimal() and command_change:
                #     raise ValueError()
                line_split_on_comma = self.lines[index].split(',')
                if 'x' in command_type:
                    if command_change:
                        x_coord = command_change
                    else:
                        x_coord = '0'
                    if not self.x_range[0] <= int(x_coord) <= self.x_range[1]:
                        invalid_range = True
                        raise ValueError()
                    self.lines[index] = f'{line_split_on_comma[0].split("(")[0]}({x_coord},{line_split_on_comma[1]}'

                elif 'y' in command_type:
                    if command_change:
                        y_coord = command_change
                    else:
                        y_coord = '0'
                    if not self.y_range[0] <= int(y_coord) <= self.y_range[1]:
                        invalid_range = True
                        raise ValueError()
                    self.lines[index] = f'{line_split_on_comma[0]}, {y_coord})'

            except ValueError:
                text_ctrl.SetForegroundColour(wx.RED)
                # not catastrophic if mouse is moved to coordinates that are out of bounds of the display size
                if not invalid_range:
                    error_msg = 'Invalid integer.'
                elif 'x' in command_type:
                    error_msg = f'The X range is {self.x_range[0]} to {self.x_range[1]} px.'
                elif 'y' in command_type:
                    error_msg = f'The Y range is {self.y_range[0]} to {self.y_range[1]} px.'
                else:
                    error_msg = f'Invalid coordinates.'
                error_static_text.SetLabel(error_msg)
                self.command_row_error = True
                event.Skip()

        elif command_type == 'type':
            self.lines[index] = f'Type:{input_one_lined}'
        elif command_type == 'wait':
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

        elif command_type == 'key':
            new_key = event.GetString()
            old_key = self.lines[index].split(' ')[1]
            self.lines[index] = self.lines[index].replace(old_key, new_key)
        elif command_type == 'key_action':
            new_action = event.GetString()
            old_action = self.lines[index].split(' ')[2]
            self.lines[index] = self.lines[index].replace(old_action, new_action)
        elif command_type == 'hotkey':
            # only cycle through last number of comboboxes because only they are the hotkey inputs
            combination = [child.GetWindow().GetStringSelection() for child in list(sizer.GetChildren()) if
                           isinstance(child.GetWindow(), wx.ComboBox)][
                          -self.num_hotkeys::]  # TODO refine method with widget names to improve reliability
            combination = eliminate_duplicates(combination)

            try:
                combination.remove('')  # remove blank hotkey placeholders
            except ValueError:
                pass

            self.lines[index] = f'Hotkey {" + ".join(combination)}'

        elif command_type == 'comment':
            self.lines[index] = f'#{input_one_lined}'
        elif command_type == 'assign_var_name':
            new_variable_name = event.GetString()

            if new_variable_name:  # do nothing if variable name is empty

                old_variable_name = variable_names_in(self.lines[index])[0]
                variable_value = assignment_variable_value_in(self.lines[index])

                self.lines[index] = f'Assign {{{{~{new_variable_name}~}}}}={variable_value}'

                # process for variable menu
                if new_variable_name not in self.variables_menu_items:  # if variable menu item does not exist
                    if old_variable_name in self.duplicate_variables:  # if variable name is unique
                        # add new variable to menu if old variable existed duplicated in another assign command
                        self.variables_menu_items[new_variable_name] = self.variables_menu.Append(wx.ID_ANY,
                                                                                                  new_variable_name)
                        self.duplicate_variables.remove(old_variable_name)
                    else:
                        # rename menu item
                        self.variables_menu_items[new_variable_name] = self.variables_menu_items.pop(old_variable_name)

                    self.variables_menu_items[new_variable_name].SetItemLabel(new_variable_name)
                    self.variables_menu_items[new_variable_name].SetHelp(f'   Insert variable {new_variable_name}.')

                    self.variables_menu_items[new_variable_name].Enable(
                        False)  # to be re-enabled when focus is bestowed upon appropriate window

                    # rebind menu item
                    self.Unbind(wx.EVT_MENU, self.variables_menu_items[new_variable_name])
                    self.Bind(wx.EVT_MENU,
                              lambda evt: self.insert_variable(evt, self.variables_menu_items[new_variable_name]),
                              self.variables_menu_items[new_variable_name])
                else:
                    self.variables_menu.DestroyItem(self.variables_menu_items[old_variable_name])  # destroy menu item
                    self.variables_menu_items.pop(old_variable_name)  # remove old variable from menu items record
                    self.duplicate_variables.append(
                        new_variable_name)  # add new (duplicate) variable to duplicate record

        elif command_type == 'assign_var_value':
            variable_name = variable_names_in(self.lines[index])[0]
            new_variable_value = input_one_lined
            self.lines[index] = f'Assign {{{{~{variable_name}~}}}}={new_variable_value}'
        elif command_type == 'conditional_var_name':
            variable_name = event.GetString()
            self.lines[
                index] = f'If {{{{~{variable_name}~}}}} {conditional_operation_in(self.lines[index], self.conditional_operations)} ~{conditional_comparison_in(self.lines[index])}~ {{'
        elif command_type == 'conditional_comparison_operator':
            comparison_operator = event.GetString()
            self.lines[
                index] = f'If {{{{~{variable_names_in(self.lines[index])[0]}~}}}} {comparison_operator} ~{conditional_comparison_in(self.lines[index])}~ {{'
        elif command_type == 'conditional_comparison_value':
            comparison_value = input_one_lined
            self.lines[
                index] = f'If {{{{~{variable_names_in(self.lines[index])[0]}~}}}} {conditional_operation_in(self.lines[index], self.conditional_operations)} ~{comparison_value}~ {{'
        elif command_type == 'loop_multiple_times_number':
            self.lines[index] = f'Loop multiple times {input_one_lined} {{'

        self.edit.ScrollChildIntoView(event.GetEventObject())

        event.Skip()

    def on_record(self):
        class RecordCtrlCounterDialog(wx.Dialog):
            def __init__(self, parent, caption):
                wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE, name='record_counter_dialog')
                self.SetTitle(caption)
                self.SetIcon(wx.Icon(parent.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.SetBackgroundColour('white')
                self.parent = parent
                self.done = False
                self.settings = import_settings()

                self.vbox = wx.BoxSizer(wx.VERTICAL)

                # add rescaled logo image
                png = wx.Image('data/record.png', wx.BITMAP_TYPE_PNG).Scale(120, 120, quality=wx.IMAGE_QUALITY_HIGH)
                icon_img = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(png))
                self.vbox.Add(icon_img, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH | wx.SOUTH, 20)

                # add main directions
                self.directions_a = wx.StaticText(self,
                                                  label=f'Start{self.parent.software_info.start_stop_directions}')
                change_font(self.directions_a, size=14)
                self.vbox.Add(self.directions_a, 0, wx.ALIGN_CENTER_HORIZONTAL)

                self.vbox.AddSpacer(15)

                # add record options collapsible pane
                self.record_collpane = wx.CollapsiblePane(self, label=' Record Options')  # ------------------------
                self.record_collpane.GetChildren()[0].SetBackgroundColour(wx.WHITE)  # set button and label background
                record_panel = self.record_collpane.GetPane()

                record_sizer = wx.StaticBoxSizer(wx.StaticBox(record_panel), wx.VERTICAL)

                from modules.aldras_record import create_record_options
                record_options_sizer = create_record_options(record_panel, settings_frame=True)

                self.FindWindowByLabel(self.settings['Record pause']).SetValue(True)
                self.FindWindowByName('some_sleep_thresh').SetValue(str(self.settings['Record pause over duration']))
                self.FindWindowByName('Record method').SetSelection(
                    self.FindWindowByName('Record method').FindString(self.settings['Record method']))

                record_sizer.Add(record_options_sizer, 0, wx.ALL, 5)
                record_panel.SetSizer(record_sizer)
                record_sizer.SetSizeHints(record_panel)
                self.vbox.Add(self.record_collpane, 0, wx.GROW)  # -------------------------------------------------

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

                self.vbox.Add(self.hbox_countdown, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, 20)
                # --------------------------------------------------------------------------------------------------

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

                self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                self.vbox_outer.Add(self.vbox, 0, wx.WEST | wx.EAST, 50)
                self.SetSizerAndFit(self.vbox_outer)
                self.Position = (
                    int(self.parent.Position[0] + ((self.parent.Size[0] - self.Size[0]) / 2)), self.parent.Position[1])
                self.finish_btn.SetFocus()

                self.thread_event_id = wx.NewIdRef()
                self.Connect(-1, -1, int(self.thread_event_id),
                             self.read_thread_event_input)  # Process message events from threads
                self.listener_thread = ListenerThread(self, record=True)
                self.listener_thread.start()
                self.Bind(wx.EVT_CLOSE, self.close_window)
                self.Center()

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
                        self.record_collpane.Show(False)

                    elif event.data == 'Action in 3 2':
                        self.countdown_light.SetLabel(' 1')
                        self.record_collpane.Show(False)

                    elif event.data == 'Action':
                        self.countdown_dark.SetForegroundColour((170, 20, 20))
                        self.directions_a.SetLabel(f'Stop{self.parent.software_info.start_stop_directions}')
                        self.countdown_light.SetLabel('')
                        self.countdown_light.Show(False)
                        self.recording_message_a.Show(True)
                        self.recording_message_b.Show(True)
                        self.record_collpane.Show(False)

                        if self.parent.settings['Notifications'] == 'Banners':
                            show_notification(self, 'Recording started', 'Perform actions to record them in Aldras')

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
                        self.Position = (int(self.position_old[0] + ((self.size_old[0] - self.Size[0]) / 2)),
                                         int(self.position_old[1]))
                    self.Fit()
                    self.Center()  # TODO center on previous position not on screen

            def finish(self, _):
                lines_recorded = self.listener_thread.abort()
                if lines_recorded:
                    record_method = self.FindWindowByName('Record method').GetStringSelection()
                    if record_method == 'Overwrite':
                        self.parent.lines = lines_recorded  # overwrite lines
                    else:
                        self.parent.lines += lines_recorded  # append lines
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

        record_count_dlg = RecordCtrlCounterDialog(self, f'Record - {self.workflow_name}')

        record_count_dlg.ShowModal()
        record_count_dlg.Destroy()

    def on_execute(self):
        class ExecuteCtrlCounterDialog(wx.Dialog):
            def __init__(self, parent, caption):
                wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)
                # wx.Frame.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_FRAME_STYLE)
                self.SetTitle(caption)
                self.SetIcon(wx.Icon(parent.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
                self.SetBackgroundColour('white')
                self.parent = parent
                self.done = False
                self.settings = import_settings()

                self.vbox = wx.BoxSizer(wx.VERTICAL)

                # add rescaled logo image
                png = wx.Image('data/execute.png', wx.BITMAP_TYPE_PNG).Scale(120, 120,
                                                                             quality=wx.IMAGE_QUALITY_HIGH)
                icon_img = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(png))
                self.vbox.Add(icon_img, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.NORTH | wx.SOUTH, 20)

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

                self.vbox.AddSpacer(15)

                self.execute_collpane = wx.CollapsiblePane(self, label=' Execution Speed',
                                                           id=wx.ID_OK)  # --------------------------
                self.execute_collpane.GetChildren()[0].SetBackgroundColour(wx.WHITE)  # set button and label background
                execute_panel = self.execute_collpane.GetPane()

                execute_sizer = wx.StaticBoxSizer(wx.StaticBox(execute_panel), wx.VERTICAL)

                from modules.aldras_execute import create_execute_options
                execute_options_sizer = create_execute_options(execute_panel, settings_frame=True)

                for setting_name in ['Execute pause between commands', 'Execute pause between commands checked',
                                     'Execute mouse command duration', 'Execute mouse command duration checked',
                                     'Interval between text character outputs',
                                     'Interval between text character outputs checked']:
                    widget = self.FindWindowByName(setting_name)

                    if isinstance(widget, wx.CheckBox):  # set true or false, not string
                        widget.SetValue(self.settings[setting_name])
                    elif isinstance(widget, wx.TextCtrl):
                        widget.SetValue(str(self.settings[setting_name]))

                execute_sizer.Add(execute_options_sizer, 0, wx.ALL, 5)

                execute_panel.SetSizer(execute_sizer)
                execute_sizer.SetSizeHints(execute_panel)
                self.vbox.Add(self.execute_collpane, 0, wx.GROW)  # ----------------------------------------------------

                # add countdown
                self.hbox_countdown = wx.BoxSizer(wx.HORIZONTAL)

                self.countdown_dark = wx.StaticText(self, label=parent.workflow_name)  # ---------------------------
                change_font(self.countdown_dark, size=22)
                self.hbox_countdown.Add(self.countdown_dark)
                self.countdown_dark.Show(False)

                self.countdown_light = wx.StaticText(self, label=parent.workflow_name)
                change_font(self.countdown_light, size=22, color=3 * (150,))
                self.hbox_countdown.Add(self.countdown_light)
                self.countdown_light.Show(False)

                self.vbox.Add(self.hbox_countdown, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, 10)
                # --------------------------------------------------------------------------------------------------

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
                self.finish_btn.SetFocus()
                self.vbox.Add(self.finish_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EAST | wx.WEST, 100)
                self.finish_btn.Show(False)

                # add in-action spacer
                self.spacer_b = wx.StaticText(self, label='')
                change_font(self.spacer_b, size=20)
                self.vbox.Add(self.spacer_b, 0, wx.ALIGN_CENTER_HORIZONTAL)

                self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
                self.vbox_outer.Add(self.vbox, 0, wx.WEST | wx.EAST, 50)
                self.SetSizerAndFit(self.vbox_outer)
                self.Position = (int(self.parent.Position[0] + ((self.parent.Size[0] - self.Size[0]) / 2)),
                                 int(self.parent.Position[1]))

                if self.settings['Notifications'] == 'Banners':
                    show_notification(self, 'Execution primed',
                                      f'Press right CTRL three times to trigger {self.parent.workflow_name} execution')

                # Process message events from threads
                self.thread_event_id = wx.NewIdRef()
                self.Connect(-1, -1, int(self.thread_event_id), self.read_thread_event_input)
                self.listener_thread = ListenerThread(self, listen_to_key=True, listen_to_mouse=False)
                self.listener_thread.start()
                self.Bind(wx.EVT_CLOSE, self.close_window)
                self.Center()

            def start_execution_thread(self):
                self.execution_pause = 0.01
                if self.FindWindowByName('Execute pause between commands checked').GetValue():
                    self.execution_pause = float(self.FindWindowByName('Execute pause between commands').GetValue())

                self.execution_mouse_dur = 0
                if self.FindWindowByName('Execute mouse command duration checked').GetValue():
                    self.execution_mouse_dur = float(self.FindWindowByName('Execute mouse command duration').GetValue())

                self.execution_type_intrv = 0
                if self.FindWindowByName('Interval between text character outputs checked').GetValue():
                    self.execution_type_intrv = float(
                        self.FindWindowByName('Interval between text character outputs').GetValue())

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
                        self.execute_collpane.Show(False)
                        self.finish_btn.Show(False)

                    elif event.data == 'Action in 3 2':
                        self.countdown_light.SetLabel(' 1')
                        self.execute_collpane.Show(False)

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
                        self.listener_thread.in_action = False
                        self.directions_a.Show(False)
                        self.directions_b.Show(False)
                        self.countdown_light.SetLabel('')
                        self.countdown_light.Show(False)
                        change_font(self.countdown_dark, size=22)
                        self.executing_message_a.Show(False)
                        self.spacer_a.Show(True)
                        self.finish_btn.Show(True)
                        self.done = True

                        if self.settings['Notifications'] == 'Banners':
                            show_notification(self, 'Execution completed',
                                              f'Aldras has completed {self.parent.workflow_name}')

                    elif event.data == 'Failsafe triggered':
                        self.execution_thread.abort()
                        self.listener_thread.in_action = False
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

                        if self.settings['Notifications'] == 'Banners':
                            show_notification(self, 'Failsafe triggered',
                                              f'{self.parent.workflow_name} execution has been halted')

                    self.vbox.Layout()
                    self.vbox_outer.Layout()
                    self.SetSizerAndFit(self.vbox_outer)
                    if self.done:
                        self.Raise()
                        self.position_old = self.GetPosition()
                        self.size_old = self.GetSize()
                        self.Position = (int(self.position_old[0] + ((self.size_old[0] - self.Size[0]) / 2)),
                                         int(self.position_old[1]))
                    self.Fit()
                    self.Center()  # TODO center on previous position not on screen

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

        command_actions = [sizer.GetChildren()[0].GetSizer().GetChildren()[2].GetWindow().GetStringSelection() for sizer
                           in self.edit_row_container_sizers if
                           len(sizer.GetChildren()[0].GetSizer().GetChildren()) > 2]

        # look for pro command actions to warn user
        if 'Pro Command' in command_actions:
            pro_command_execution_warning_dlg = wx.MessageDialog(None,
                                                                 'Execution may not proceed as expected.\n\nOne or more professional-level commands have been detected. Would you like to continue?',
                                                                 'Workflow Professional Command Detected',
                                                                 wx.YES_NO | wx.ICON_WARNING)

            if pro_command_execution_warning_dlg.ShowModal() == wx.ID_NO:
                return

        execute_count_dlg = ExecuteCtrlCounterDialog(self, f'Execute - {self.workflow_name}')

        execute_count_dlg.ShowModal()
        execute_count_dlg.Destroy()

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
            try:
                return command_row_sizeritem.GetChildren()[0].GetSizer().GetChildren()[1].GetSizer().GetChildren()[
                    up_down_index].GetWindow().Show(show)
            except AttributeError:
                print('AttributeError  2925118694')

    # do_nothing = lambda: None
    @staticmethod
    def do_nothing(_):  # might want to use to redirect scroll inputs
        """Function to bind events to be disabled."""
        pass  # TODO replace with scrolling functionality of panel at some point

    def save_to_file(self):
        """Write to workflow file"""

        workflow_path_when_launched = self.parent.workflow_path_name

        if self.features_unlocked and workflow_path_when_launched[-4:] == '.txt':
            with open(workflow_path_when_launched, 'w') as record_file:
                record_file.write(f'HardwareID: {hardware_id}\n')  # record hardware id
                for line in self.lines:
                    record_file.write(f'{line}\n')

        else:
            self.parent.recent_workflows.remove(workflow_path_when_launched)
            workflow_path_when_launched = workflow_path_when_launched.replace('.txt', '.aldras')
            self.parent.recent_workflows.insert(0, workflow_path_when_launched)
            self.parent.update_recent_workflows()
            with open(workflow_path_when_launched, 'w') as record_file:
                hardware_id_text = f'HardwareID: {hardware_id}\n'
                record_file.write(f'{fernet.encrypt(hardware_id_text.encode()).decode()}\n')
                for line in self.lines:
                    record_file.write(f'{fernet.encrypt(line.encode()).decode()}\n')

        if self.workflow_name_when_launched != self.workflow_name:  # if workflow was renamed
            workflow_path_new = workflow_path_when_launched.replace(self.workflow_name_when_launched,
                                                                    self.workflow_name)
            self.parent.workflow_path_name = workflow_path_new
            os.rename(workflow_path_when_launched, workflow_path_new)
            self.parent.recent_workflows = eliminate_duplicates(self.parent.recent_workflows)
            self.parent.recent_workflows.remove(workflow_path_when_launched)
            self.parent.recent_workflows.insert(0, workflow_path_new)
            self.parent.update_recent_workflows()
            self.workflow_name_when_launched = self.workflow_name

        self.lines_when_launched = self.lines

    def save_workflow(self):
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

            save_dlg = SaveDialog(self).ShowModal()
            if save_dlg == wx.ID_OK:
                self.save_to_file()
            elif save_dlg == 20:  # 'don't save' button
                pass
            else:  # cancel button
                return 'cancel'

    def delete_workflow(self):
        """Delete workflow file"""
        confirm_deletion_dlg = wx.MessageDialog(None, f'Would you like to delete "{self.workflow_name}"?',
                                                'Workflow Deletion Confirmation', wx.YES_NO | wx.ICON_INFORMATION)

        if confirm_deletion_dlg.ShowModal() == wx.ID_YES:
            # save file to process any name changes
            self.save_to_file()

            # delete file and remove from recent workflows
            if os.path.exists(self.parent.workflow_path_name):
                os.remove(self.parent.workflow_path_name)

                self.parent.recent_workflows.remove(self.parent.workflow_path_name)
                self.parent.update_recent_workflows()

            self.close_window()

    def full_refresh(self):
        """Relaunch EditFrame with same workflow lines"""
        new_edit_frame = EditFrame(self.parent, [f'HardwareID: {hardware_id}'] + self.lines,
                                   show_frame=False, previous_lines_when_launched=self.lines_when_launched)
        new_edit_frame.Size = self.Size
        new_edit_frame.Position = self.Position
        new_edit_frame.Show()
        self.Destroy()

    def close_window(self, _=None, quitall=False):
        if self.save_workflow() == 'cancel':
            return

        self.Hide()
        if quitall:
            # close entire application include SelectionFrame
            self.parent.Close(True)
        else:
            # center workflow frame where edit frame is now
            self.parent.Position = (int(self.Position[0] + ((self.Size[0] - self.parent.Size[0]) / 2)),
                                    int(self.Position[1] + ((self.Size[1] - self.parent.Size[1]) / 2)))
            self.parent.Show()
            self.parent.Raise()
            self.parent.Layout()


class SelectionFrame(wx.Frame):
    """Main frame to select workflow."""

    def __init__(self, parent, license_type):

        class SoftwareInfo:
            """Object to contain all information about Aldras."""

            def __init__(self, features_unlocked):
                self.name = 'Aldras'
                self.version = '2021.4'
                self.data_directory = 'data/'
                self.icon = f'{self.data_directory}{self.name.lower()}.ico'  # should be data/aldras.ico
                self.png = f'{self.data_directory}{self.name.lower()}.png'  # should be data/aldras.png
                self.copyright = f'2019-2021 {self.name}'
                self.website = f'https://www.{self.name.lower()}.com/'
                self.description = f'{self.name} is a simple and intuitive automation tool that can drastically\nimprove the efficiency of processes with repetitive computer tasks.'
                self.start_stop_directions = ': Press the right control key 3 times'
                self.advanced_edit_guide_description = f'A look at the underlying syntax of {self.name} commands.'
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
                    'If {{~"variable"~}} "operation" ~"comparison"~ {\n\t"commands"\n  }': [
                        'If {{~diameter~}} < ~10~ {\n     Type:The circle is small.\n   }',
                        'Executes containing commands if conditional is satisfied']
                    # need to add scrolled panel to advanced edit guide
                    # 'Loop "behavior" {\n         "commands"\n}': [
                    #     'Loop multiple times 5 {\n     Type:This will be executed 5 times.\n   }',
                    #     #"Loop for each element in list [1`'`2`'`3`'`4`'`5] {\n     Type:This will be executed 5 times, with loop.var having a value of 1 through 5 depending on the loop iteration.\n   }"],
                    #     'Executes containing commands in a repetitive loop']
                }
                self.advanced_edit_guide_commands.update(self.advanced_edit_guide_commands_pro)
                self.advanced_edit_guide_website = f'{self.website}/edit-guide'

                self.commands = ['Mouse button', 'Type', 'Wait', 'Special key', 'Function key', 'Media key', 'Hotkey',
                                 'Mouse-move', 'Double-click', 'Triple-click', 'Comment']
                if features_unlocked:
                    self.commands.extend(['Assign', 'Conditional', 'Loop'])
                else:
                    self.commands.extend(['Pro Command'])

                self.mouse_buttons = ['Left', 'Right']
                self.mouse_actions = ['Click', 'Press', 'Release']
                self.key_actions = ['Tap', 'Press', 'Release']
                self.special_keys = ['Backspace', 'Del', 'Enter', 'Tab', 'Left', 'Right', 'Up', 'Down', 'Home', 'End',
                                     'PageUp', 'PageDown', 'Space', 'Shift', 'Esc', 'Ctrl', 'Alt', 'Win', 'Command',
                                     'Option', 'BrowserBack', 'BrowserForward', 'Insert', 'NumLock', 'PrntScrn',
                                     'ScrollLock', 'Pause']
                self.media_keys = ['PlayPause', 'NextTrack', 'PrevTrack', 'VolumeMute', 'VolumeUp', 'VolumeDown']
                self.function_keys = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
                self.alphanum_keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                                      'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5',
                                      '6', '7', '8', '9', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',',
                                      '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
                                      '{', '|', '}', '~']
                self.all_keys = [''] + self.special_keys + self.alphanum_keys + self.function_keys + self.media_keys

        self.license_type = license_type
        self.features_unlocked = any(x in license_type for x in advanced_feature_license_types)
        self.software_info = SoftwareInfo(self.features_unlocked)
        self.settings = import_settings()
        wx.Frame.__init__(self, parent, title=f'{self.software_info.name} Automation', name='selection_frame')
        setup_frame(self)
        print(f'LICENSE type: {self.license_type}')

        self.workflow_directory = self.settings['Workflow folder']
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
        self.workflow_name_input = PlaceholderTextCtrl(self.workflow_panel, wx.ID_ANY, placeholder='Workflow name',
                                                       size=(200, -1),
                                                       style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_ok, self.workflow_name_input)
        self.vbox.Add(self.workflow_name_input, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, self.padding_y)

        # add recent workflow title
        self.vbox_recent = wx.BoxSizer(wx.VERTICAL)
        self.recent_title = wx.StaticText(self.workflow_panel, label='Recent')
        change_font(self.recent_title, size=10, style=wx.ITALIC, color=3 * (120,))
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
        self.ok_btn.SetFocus()
        self.Center()
        self.Show()
        self.check_for_updates()

    def check_for_updates(self):
        if check_internet_connection():
            try:
                html_page = requests.get('https://aldras.netlify.com/assets/html/download_section').text
                soup = BeautifulSoup(html_page, features='html.parser')

                for link in soup.findAll('a'):  # loop through all links
                    link_text = link.get('href')
                    if '../../downloads/aldras-setup-' in link_text:  # if link has setup executable structure
                        version_and_extension = link_text.replace('../../downloads/aldras-setup-', '')
                        latest_version = version_and_extension.replace('.exe', '')
                        latest_version = latest_version.replace('-', '.')

                        if float_in(self.software_info.version) < float_in(latest_version):
                            # there is a newer version available

                            update_available_dlg = wx.MessageDialog(None,
                                                                    f'Aldras version {latest_version} is now available!\n\nWould you like to download the update?',
                                                                    'Aldras Update Available',
                                                                    wx.YES_NO | wx.ICON_INFORMATION | wx.CENTRE)

                            update_available_dlg.SetYesNoLabels('Download',
                                                                'Later')  # rename 'Yes' and 'No' labels to 'Download' and 'Later'

                            if update_available_dlg.ShowModal() == wx.ID_YES:
                                # download_link = 'https://aldras.netlify.com/downloads/aldras-setup-' + version_and_extension
                                download_link = 'https://aldras.netlify.com/download'
                                webbrowser.open_new_tab(download_link)
            except Exception:
                pass

    def update_recent_workflows(self):
        self.recent_workflows = eliminate_duplicates(self.recent_workflows)
        with open(self.data_directory_recent_workflows, 'w') as record_file:  # add workflow to recent history
            for line in self.recent_workflows[0:20]:
                record_file.write(f'{line}\n')

        self.hbox_recent.ShowItems(show=False)
        self.hbox_recent.Clear(delete_windows=True)

        # show recent workflow title if there are recent workflows
        if self.recent_workflows and self.settings['Number of recent workflows displayed']:
            self.recent_title.Show()

        # create buttons for most recently accessed workflows
        for workflow_path_name in self.recent_workflows[0:self.settings['Number of recent workflows displayed']]:
            workflow_name = ntpath.basename(workflow_path_name).replace('.txt', '').replace('.aldras', '')
            self.recent_workflow_btn = wx.Button(self.workflow_panel, wx.ID_ANY, label=workflow_name)
            self.recent_workflow_btn.Bind(wx.EVT_BUTTON,
                                          lambda event, workflow_path_trap=workflow_path_name: launch_workflow(self,
                                                                                                               workflow_path_trap,
                                                                                                               recent_launch=True))
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
            # workflow confirmation if entry is default
            confirm_workflow_dlg = wx.MessageDialog(None,
                                                    f'Please confirm that "{self.workflow_name_input.GetValue().capitalize()}" is your desired workflow.',
                                                    f'{self.software_info.name} Workflow Confirmation',
                                                    wx.YES_NO | wx.ICON_INFORMATION)

            if confirm_workflow_dlg.ShowModal() == wx.ID_YES:
                launch_workflow(self,
                                workflow_path_name=f'{self.workflow_directory}\\{self.workflow_name_input.GetValue().capitalize()}.txt')

    def restart(self):
        SelectionFrame(None, self.license_type)
        self.Destroy()

    def on_exit(self, _):
        # trigger close event
        self.Close(True)


if __name__ == '__main__':
    mouse_monitor_frame = None
    adv_edit_guide = None
    sys.excepthook = exception_handler

    fernet = Fernet(b'hIYvMZaPz2ISuLmLXspJDwQNJVB_0D-d-Ftjm0eGSFo=')
    advanced_feature_license_types = ['professional', 'trial']  # these license types get access to unlockable features

    app = wx.App(False)

    if system_platform() == 'Windows':
        SelectionFrame(None, 'professional')

    else:
        wx.MessageDialog(None,
                         'Unfortunately at this time, Aldras has only\nbeen tested and released for use on Windows.',
                         'Incompatible Operating System', wx.OK | wx.ICON_WARNING).ShowModal()

    app.MainLoop()
