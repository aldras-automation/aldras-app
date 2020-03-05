import os

import wx
import wx.adv
import wx.lib.scrolledpanel


def create_about_frame(self):
    about_info = wx.adv.AboutDialogInfo()
    about_info.SetName('Aldras Automation')
    about_info.SetIcon(wx.Icon('logo.ico'))
    about_info.SetVersion(self.software_version)
    about_info.SetDescription('Simple, powerful utility for general computer automation.')
    about_info.SetCopyright('(C) 2020 (Not yet)')
    about_info.SetWebSite('http://www.alderas.com')
    wx.adv.AboutBox(about_info)


def setup_frame(self):
    # setting up the file menu
    file_menu = wx.Menu()
    menu_about = file_menu.Append(wx.ID_ABOUT, 'About', ' Information about Aldras')
    # menu_open = file_menu.Append(wx.ID_OPEN, 'Open', ' Open a file to edit')

    # creating the menu bar
    menu_bar = wx.MenuBar()
    menu_bar.Append(file_menu, 'File')  # Adding the file menu to the menu bar
    self.SetMenuBar(menu_bar)  # adding the menu bar to the Frame)
    self.Bind(wx.EVT_MENU, self.on_about, menu_about)
    # self.Bind(wx.EVT_MENU, self.OnOpen, menu_open

    # assign icon
    self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))

    # set background color
    self.SetBackgroundColour('white')


def coords_of(line):
    coords = line.split('(')[1].replace(' ', '').replace(')', '').split(',')
    coords = (int(coords[0]), int(coords[1]))
    return coords


class CustomError(Exception):
    pass


class PlaceholderTextCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        self.default_text = kwargs.pop('placeholder', '')
        wx.TextCtrl.__init__(self, *args, **kwargs)
        self.on_unfocus(None)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_unfocus)

    def on_focus(self, evt):
        self.SetForegroundColour(wx.BLACK)
        if self.GetValue() == self.default_text:
            self.SetValue('')
        evt.Skip()

    def on_unfocus(self, evt):
        if self.GetValue().strip() == '':
            self.SetValue(self.default_text)
            self.SetForegroundColour(wx.LIGHT_GREY)
        if evt:
            evt.Skip()


class EditFrame(wx.Frame):
    def __init__(self, parent, title, workflow_name):
        self.dirname = ''
        wx.Frame.__init__(self, parent, title=title)

        setup_frame(self)

        # set margin
        self.margins = 10

        # set software version
        self.software_version = '2020.0.0 Beta'

        # create sizers
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.hbox_outer = wx.BoxSizer(wx.HORIZONTAL)

        # create north and west margins
        # self.vbox_outer.AddSpacer(self.margin_y)
        # self.hbox_outer.AddSpacer(self.margin_x)

        # add top panel
        self.hbox_top = wx.BoxSizer(wx.HORIZONTAL)

        # add back button
        self.back_btn = wx.Button(self, size=wx.Size(50, -1), label='<')
        self.back_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_back(parent))
        self.hbox_top.Add(self.back_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        self.hbox_top.AddSpacer(10)

        # add workflow title
        self.title = wx.StaticText(self, label='Workflow: {}'.format(workflow_name))
        self.title.SetFont(wx.Font(wx.FontInfo(20)))  # change font size
        self.title_contrast = 60
        self.title.SetForegroundColour(
            (self.title_contrast, self.title_contrast, self.title_contrast))  # change font color to (r,g,b)
        self.hbox_top.Add(self.title, 0, wx.ALIGN_CENTER_VERTICAL)

        self.vbox_outer.Add(self.hbox_top)

        self.vbox_outer.AddSpacer(10)

        # ------------------------------------------------------------------------------------------- bottom sizer
        self.hbox_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.fg_bottom = wx.FlexGridSizer(1, 2, 10, 10)

        # add edit panel
        self.edit = wx.lib.scrolledpanel.ScrolledPanel(self, style=wx.SIMPLE_BORDER, size=(500, 300))
        self.edit.SetupScrolling()

        # create sizer
        self.vbox_edit = wx.BoxSizer(wx.VERTICAL)

        self.edit.SetSizer(self.vbox_edit)

        self.commands = ['Mouse button', 'Type', 'Sleep', 'Special key', 'Function key', 'Media key', 'Hotkey',
                         'Mouse-move', 'Double-click', 'Triple-click', 'Scroll']
        self.mouse_buttons = ['Left', 'Right']
        self.mouse_actions = ['Tap', 'Press', 'Release']
        self.coord_width = 40
        self.special_keys = ['Backspace', 'Del', 'Enter', 'Tab', 'Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Pgup',
                             'Pgdn', 'Space', 'Shift', 'Esc', 'Ctrl', 'Alt', 'Win', 'Cmd', 'Option', 'Back nav',
                             'Capslock', 'Insert', 'Numlock', 'Prtscrn', 'Scrlock']
        self.media_keys = ['Playpause', 'Nexttrack', 'Prevtrack', 'Volmute', 'Voldown', 'Volup']
        self.function_keys = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
        self.alphanum_keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                              'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                              '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<',
                              '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', ' ']
        self.all_keys = self.special_keys + self.alphanum_keys + self.media_keys + self.alphanum_keys

        # read or create workflow file
        try:
            with open('{}.txt'.format(workflow_name), 'r') as record_file:
                self.lines = record_file.readlines()
        except FileNotFoundError:  # create file if not found
            with open('{}.txt'.format(workflow_name), 'w'):
                self.lines = []

        print('lines: {}'.format(self.lines))

        for self.line in self.lines:
            self.hbox_edit = wx.BoxSizer(wx.HORIZONTAL)
            if '#' in self.line:  # workflow comment so no action
                pass
            else:
                self.line = self.line.replace('\n', '').lower()
                self.vbox_edit.AddSpacer(5)
                self.hbox_edit = wx.BoxSizer(wx.HORIZONTAL)
                self.hbox_edit.AddSpacer(5)
                self.line_first_word = self.line.split(' ')[0]
                if '-mouse' in self.line_first_word:
                    self.command = wx.ComboBox(self.edit, value='Mouse button', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command)

                    if 'left' in self.line_first_word:
                        self.mouse_button = wx.ComboBox(self.edit, value='Left', choices=self.mouse_buttons,
                                                        style=wx.CB_READONLY)
                    elif 'right' in self.line_first_word:
                        self.mouse_button = wx.ComboBox(self.edit, value='Right', choices=self.mouse_buttons,
                                                        style=wx.CB_READONLY)
                    else:
                        raise CustomError('Mouse button not specified.')
                    self.hbox_edit.AddSpacer(10)
                    self.hbox_edit.Add(self.mouse_button)

                    if 'tap' in self.line:
                        self.mouse_action = wx.ComboBox(self.edit, value='Tap', choices=self.mouse_actions,
                                                        style=wx.CB_READONLY)
                    elif 'press' in self.line:
                        self.mouse_action = wx.ComboBox(self.edit, value='Press', choices=self.mouse_actions,
                                                        style=wx.CB_READONLY)
                    elif 'release' in self.line:
                        self.mouse_action = wx.ComboBox(self.edit, value='Release', choices=self.mouse_actions,
                                                        style=wx.CB_READONLY)
                    else:
                        raise CustomError('Mouse action not specified.')
                    self.hbox_edit.AddSpacer(10)
                    self.hbox_edit.Add(self.mouse_action)

                    self.hbox_edit.AddSpacer(10)
                    self.label = wx.StaticText(self.edit, label='at pt. (  ')
                    self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.x_coord = None  # redefined in self.create_point_input(self.line) method
                    self.y_coord = None  # redefined in self.create_point_input(self.line) method
                    self.create_point_input(self.line)

                elif 'type:' in self.line_first_word:
                    self.command = wx.ComboBox(self.edit, value='Type', choices=self.commands, style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command)
                    self.hbox_edit.AddSpacer(10)
                    self.text_to_type = wx.TextCtrl(self.edit,
                                                    value=str(self.line.replace('type: ', '').replace('Type: ', '')))
                    self.hbox_edit.Add(self.text_to_type)
                    # self.hbox_edit.Add(self.text_to_type, 1, wx.EXPAND)

                elif 'sleep' in self.line_first_word:
                    self.command = wx.ComboBox(self.edit, value='Sleep', choices=self.commands, style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command)

                    self.hbox_edit.AddSpacer(10)

                    self.sleep_time = wx.TextCtrl(self.edit, value=str(self.line.split(' ')[-1]))
                    self.hbox_edit.Add(self.sleep_time)
                    # self.hbox_edit.Add(self.sleep_time, 1, wx.EXPAND)

                elif 'hotkey' in self.line_first_word:
                    self.command = wx.ComboBox(self.edit, value='Hotkey', choices=self.commands, style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command)

                    self.combination = [x.capitalize() for x in
                                        self.line.replace('hotkey', '').replace(' ', '').split('+')]

                    # print(self.combination)

                    self.hbox_edit.AddSpacer(10)

                    self.counter = 0
                    for self.key in self.combination:
                        self.counter += 1

                        self.hotkey_cb = wx.ComboBox(self.edit, value=str(self.key), choices=self.all_keys,
                                                     style=wx.CB_READONLY)
                        self.hbox_edit.Add(self.hotkey_cb)

                        if self.counter < len(self.combination):
                            self.label = wx.StaticText(self.edit, label='  +  ')
                            self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                elif 'key' in self.line_first_word:
                    self.key_in = self.line.split(' ')[1]
                    self.key = None  # redefined in self.create_key_combo_box(command) method
                    if self.key_in in [x.lower() for x in self.special_keys]:
                        self.create_key_combo_box('Special Key')

                    elif self.key_in in [x.lower() for x in self.function_keys]:
                        self.create_key_combo_box('Function Key')

                    elif self.key_in in [x.lower() for x in self.media_keys]:
                        self.create_key_combo_box('Media Key')

                    else:
                        self.unknown_key_message = wx.StaticText(self.edit,
                                                                 label='**Unknown key from line: \"{}\"'.format(
                                                                     self.line))
                        self.unknown_key_message.SetFont(
                            wx.Font(9, wx.DEFAULT, wx.ITALIC, wx.NORMAL))  # change font size
                        self.unknown_key_message_contrast = 70
                        self.unknown_key_message.SetForegroundColour(
                            (self.unknown_key_message_contrast, self.unknown_key_message_contrast,
                             self.unknown_key_message_contrast))  # change font color to (r,g,b)
                        self.hbox_edit.Add(self.unknown_key_message, 1, wx.ALIGN_CENTER_VERTICAL)

                elif ('mouse' in self.line_first_word) and ('move' in self.line_first_word):
                    self.command = wx.ComboBox(self.edit, value='Mouse-move', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command)

                    self.hbox_edit.AddSpacer(10)
                    self.label = wx.StaticText(self.edit, label='to pt. (  ')
                    self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.x_coord = None  # redefined in self.create_point_input(self.line) method
                    self.y_coord = None  # redefined in self.create_point_input(self.line) method
                    self.create_point_input(self.line)

                elif ('double' in self.line) and ('click' in self.line):
                    self.command = wx.ComboBox(self.edit, value='Double-click', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command)

                    self.hbox_edit.AddSpacer(10)
                    self.label = wx.StaticText(self.edit, label='at pt. (  ')
                    self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.x_coord = None  # redefined in self.create_point_input(self.line) method
                    self.y_coord = None  # redefined in self.create_point_input(self.line) method
                    self.create_point_input(self.line)

                elif ('triple' in self.line) and ('click' in self.line):
                    self.command = wx.ComboBox(self.edit, value='Triple-click', choices=self.commands,
                                               style=wx.CB_READONLY)
                    # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                    self.hbox_edit.Add(self.command)

                    self.hbox_edit.AddSpacer(10)
                    self.label = wx.StaticText(self.edit, label='at pt. (  ')
                    self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.x_coord = None  # redefined in self.create_point_input(self.line) method
                    self.y_coord = None  # redefined in self.create_point_input(self.line) method
                    self.create_point_input(self.line)

                else:
                    self.hbox_edit.AddSpacer(10)
                    self.unknown_command_message = wx.StaticText(self.edit,
                                                                 label='**Unknown command from line: \"{}\"'.format(
                                                                     self.line))
                    self.unknown_command_message.SetFont(
                        wx.Font(9, wx.DEFAULT, wx.ITALIC, wx.NORMAL))  # change font size
                    self.unknown_command_message_contrast = 70
                    self.unknown_command_message.SetForegroundColour(
                        (self.unknown_command_message_contrast, self.unknown_command_message_contrast,
                         self.unknown_command_message_contrast))  # change font color to (r,g,b)
                    self.hbox_edit.Add(self.unknown_command_message, 0, wx.ALIGN_CENTER_VERTICAL)

                self.vbox_edit.Add(self.hbox_edit)
                # self.vbox_edit.Add(self.hbox_edit, 1, wx.EXPAND)
                self.vbox_edit.AddSpacer(5)
                self.vbox_edit.Add(wx.StaticLine(self.edit, -1), 0, wx.EXPAND)

        # ------------------------------------------------------------------------------------------- action strip sizer

        self.vbox_action = wx.BoxSizer(wx.VERTICAL)
        self.hbox_line_mods = wx.BoxSizer(wx.HORIZONTAL)

        # add minus command button
        self.minus_btn = wx.Button(self, label='-', size=(20, -1))
        # self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_back(parent))
        self.hbox_line_mods.Add(self.minus_btn, 1, wx.EXPAND)

        self.hbox_line_mods.AddSpacer(5)

        # add plus command button
        self.plus_btn = wx.Button(self, label='+', size=(20, -1))
        # self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_back(parent))
        self.hbox_line_mods.Add(self.plus_btn, 1, wx.ALIGN_RIGHT)

        self.vbox_action.Add(self.hbox_line_mods, 0, wx.EXPAND)

        self.vbox_action.AddSpacer(10)

        # add advanced command button
        self.advanced_btn = wx.Button(self, label='Advanced')
        # self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_back(parent))
        self.vbox_action.Add(self.advanced_btn, 0, wx.EXPAND)

        self.vbox_action.AddStretchSpacer()

        # add record command button
        self.record_btn = wx.Button(self, label='Record')
        # self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_back(parent))
        self.vbox_action.Add(self.record_btn, 0, wx.EXPAND)

        self.vbox_action.AddSpacer(10)

        # add execute command button
        self.execute_btn = wx.Button(self, label='Execute')
        # self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_back(parent))
        self.vbox_action.Add(self.execute_btn, 0, wx.ALIGN_BOTTOM | wx.EXPAND)

        self.fg_bottom.AddMany([(self.edit, 1, wx.EXPAND), (self.vbox_action, 1, wx.EXPAND)])
        self.fg_bottom.AddGrowableCol(0, 0)
        self.fg_bottom.AddGrowableRow(0, 0)

        self.vbox_outer.Add(self.fg_bottom, 1, wx.EXPAND)
        # self.vbox_outer.Add(self.fg_bottom, proportion=2, flag=wx.ALL | wx.EXPAND, border=15)

        # -------------------------------------------------------------------------------------------

        # add margins and inside sizers
        self.vbox_outer.AddSpacer(5)
        self.hbox_outer.Add(self.vbox_outer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, self.margins)
        self.hbox_outer.SetSizeHints(self)
        self.SetSizer(self.hbox_outer)
        self.Show()

    def on_back(self, parent):
        parent.Show()
        self.Close()  # close the frame

    def on_about(self, event):
        create_about_frame(self)

    def create_key_combo_box(self, command):
        self.command = wx.ComboBox(self.edit, value=command, choices=self.commands, style=wx.CB_READONLY)
        # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        self.hbox_edit.Add(self.command)

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

        self.hbox_edit.Add(self.key)

    def create_point_input(self, line):
        self.x_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE, size=wx.Size(self.coord_width, -1),
                                   value=str(coords_of(line)[0]))  # TODO validator
        self.hbox_edit.Add(self.x_coord)

        self.label = wx.StaticText(self.edit, label=' , ')
        self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

        self.y_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE, size=wx.Size(self.coord_width, -1),
                                   value=str(coords_of(line)[1]))  # , validator_float)
        self.hbox_edit.Add(self.y_coord)

        self.label = wx.StaticText(self.edit, label='  )')
        self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)


class WorkflowFrame(wx.Frame):
    def __init__(self, parent, title):
        self.dirname = ''
        wx.Frame.__init__(self, parent, title=title)

        setup_frame(self)

        # add encompassing panel
        self.container = wx.Panel(self)

        # set margins
        self.margin_y = 25
        self.margin_x = 100

        # set padding
        self.padding_y = 25
        self.padding_x = 100

        # set software version
        self.software_version = '2020.0.0 Beta'

        # create sizers
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.hbox_outer = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # create north and west margins
        self.vbox_outer.AddSpacer(self.margin_y)
        self.hbox_outer.AddSpacer(self.margin_x)

        # add rescaled logo image
        png = wx.Image('logo.png', wx.BITMAP_TYPE_PNG).Scale(150, 150, wx.IMAGE_QUALITY_BICUBIC)
        self.logo_img = wx.StaticBitmap(self.container, wx.ID_ANY, wx.Bitmap(png))
        self.vbox.Add(self.logo_img, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program name text
        self.program_name = wx.StaticText(self.container, label='Aldras Automation')
        self.program_name.SetFont(wx.Font(wx.FontInfo(18)))  # change font
        self.program_name_contrast = 60
        self.program_name.SetForegroundColour((self.program_name_contrast, self.program_name_contrast,
                                               self.program_name_contrast))  # change font color to (r,g,b)
        self.vbox.Add(self.program_name, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program version text
        self.program_version = wx.StaticText(self.container, label='Version {}'.format(self.software_version))
        self.program_version.SetFont(wx.Font(wx.FontInfo(10)).Italic())  # change font
        self.program_version_contrast = 150
        self.program_version.SetForegroundColour((self.program_version_contrast, self.program_version_contrast,
                                                  self.program_version_contrast))  # change font color to (r,g,b)
        self.vbox.Add(self.program_version, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.AddSpacer(self.padding_y)

        # add input field for the workflow name
        self.workflow_name_input = PlaceholderTextCtrl(self.container, -1, placeholder='Workflow', size=(200, -1))
        self.vbox.Add(self.workflow_name_input, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.AddSpacer(self.padding_y)

        self.hbox_outer.Add(self.vbox)

        # add east margin
        self.hbox_outer.AddSpacer(self.margin_x)

        self.vbox_outer.AddStretchSpacer()
        self.vbox_outer.Add(self.hbox_outer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox_outer.AddStretchSpacer()

        self.button_array = wx.StdDialogButtonSizer()
        self.cancel_btn = wx.Button(self.container, label='Quit')
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_exit)
        self.button_array.Add(self.cancel_btn)
        self.ok_btn = wx.Button(self.container, label='OK')
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_open_frame)
        self.button_array.Add(self.ok_btn)
        self.vbox_outer.Add(self.button_array, 0, wx.ALIGN_RIGHT)

        # add south margin
        self.vbox_outer.AddSpacer(5)

        self.container.SetSizer(self.vbox_outer)
        self.vbox_outer.SetSizeHints(self)

        self.ok_btn.SetFocus()
        self.Show()

    def on_about(self, event):
        create_about_frame(self)

    def on_exit(self, event):
        self.Close(True)  # close the frame

    def on_open_frame(self, event):
        # directory selector
        # dlg = wx.DirDialog(None, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        # if dlg.ShowModal() == wx.ID_OK:
        #     fdir = dlg.GetPath() + "/"
        #     dlg.SetPath(fdir)
        #     print('You selected: %s\n' % dlg.GetPath())
        # dlg.Destroy()
        if self.workflow_name_input.GetValue() == 'd':
            # create a message dialog box
            dlg = wx.MessageDialog(self,
                                   'Invalid file name.\nPlease try again.',
                                   'Invalid File Name', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()  # show modal
            dlg.Destroy()  # destroy dialog when finished
        else:
            dlg = wx.MessageDialog(None, 'Please confirm that "{}" is your desired workflow.'.format(
                self.workflow_name_input.GetValue()), 'Workflow Name Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()

            if result == wx.ID_YES:
                # main_frame = EditFrame(None,
                #                        'Aldras Automation - Workflow: {}'.format(self.workflow_name_input.GetValue()),
                #                        self.workflow_name_input.GetValue())
                self.Hide()
                EditFrame(self, 'Aldras Automation - Workflow: {}'.format(self.workflow_name_input.GetValue()),
                          self.workflow_name_input.GetValue())
                # main_frame.Show()
                # time.sleep(2)
                # self.Show()
                # self.Close(True)  # close the frame
            else:
                pass  # returns user back to workflow window

    def on_open(self, e):
        """ Open a file"""
        dlg = wx.FileDialog(self, 'Choose a file', self.dirname, '', '*.*', wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.workflow_name_input.SetValue(f.read())
            f.close()
        dlg.Destroy()


def main():
    app = wx.App(False)
    frame = WorkflowFrame(None, 'Aldras Automation')
    app.MainLoop()


if __name__ == '__main__':
    main()
