import os

import wx
import wx.adv
import wx.lib.scrolledpanel


# TODO investigate image buttons (edit frame - back button)
# TODO alternate row shading (edit frame)
# TODO command move
# TODO menu bar exit option
# TODO control key validation
# TODO re-runs
# TODO create help guide
# TODO investigate compilation speed increases (numba, cpython, pypy)
# TODO investigate speed optimization by converting lists to sets used for 'in' comparisons
# TODO premium feature separation (any workflow destination)


def do_nothing(event=None):
    pass


def eliminate_duplicates(list_with_duplicates):
    seen = set()
    seen_add = seen.add
    return [x for x in list_with_duplicates if not (x in seen or seen_add(x))]


def create_about_frame(self):
    about_info = wx.adv.AboutDialogInfo()
    about_info.SetName('{} Automation'.format(self.software_info.name))
    about_info.SetIcon(wx.Icon('logo.ico'))
    about_info.SetVersion(self.software_info.version)
    about_info.SetDescription('Simple, powerful utility for general computer automation.')
    about_info.SetCopyright('(C) 2020 (Not yet)')
    about_info.SetWebSite(self.software_info.website)
    wx.adv.AboutBox(about_info)


def setup_frame(self, status_bar=False):
    if status_bar:
        self.CreateStatusBar()

    # setting up the file menu
    file_menu = wx.Menu()
    menu_about = file_menu.Append(wx.ID_ABOUT, 'About', ' Information about {}'.format(self.software_info.name))
    menu_exit = file_menu.Append(wx.ID_EXIT, 'Exit', 'Exit {}'.format(self.software_info.name))

    # menu_open = file_menu.Append(wx.ID_OPEN, 'Open', ' Open a file to edit')

    # creating the menu bar
    menu_bar = wx.MenuBar()
    menu_bar.Append(file_menu, 'File')  # Adding the file menu to the menu bar
    self.SetMenuBar(menu_bar)  # adding the menu bar to the Frame)
    self.Bind(wx.EVT_MENU, lambda event: on_about(self), menu_about)
    self.Bind(wx.EVT_MENU, lambda event: on_exit(self), menu_exit)

    # self.Bind(wx.EVT_MENU, self.OnOpen, menu_open)

    # assign icon
    self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))

    # set background color
    self.SetBackgroundColour('white')

    def on_about(self):
        create_about_frame(self)

    def on_exit(self):
        self.Close()


def coords_of(line):
    coords = line.split('(')[1].replace(' ', '').replace(')', '').split(',')
    coords = (int(coords[0]), int(coords[1]))
    return coords


def update_status_bar(parent, status):
    parent.StatusBar.SetStatusText(status)


def clear_status_bar(parent):
    parent.StatusBar.SetStatusText('')


def config_status_and_tooltip(parent, obj_to_config, status, tooltip=None):
    obj_to_config.Bind(wx.EVT_ENTER_WINDOW, lambda event: update_status_bar(parent, '   ' + status))
    obj_to_config.Bind(wx.EVT_LEAVE_WINDOW, lambda event: clear_status_bar(parent))
    if tooltip is None:
        obj_to_config.SetToolTip(status)
    elif not tooltip:
        pass
    else:
        obj_to_config.SetToolTip(tooltip)


class SoftwareInfo:
    def __init__(self):
        self.name = 'Aldras'
        self.version = '2020.0.0 Beta'
        self.website = 'http://www.{}.com'.format(self.name.lower())
        self.advanced_edit_guide_website = '{}/edit-guide'.format(self.website)
        self.advanced_edit_guide_description = self.name + ' is not sensitive capitalization upon ingest,\nplease use whatever convention is most readable for you.'
        self.advanced_edit_guide_command_description = 'Replace the values in the curly brackets { }.'
        self.advanced_edit_guide_commands = {
            '{Left/Right}-mouse {tap/press/release} at ({x}, {y})': ['Left-mouse tap at (284, 531)',
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


class CustomError(Exception):
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
        event.Skip()

    def on_unfocus(self, event):
        if self.GetValue().strip() == '':
            self.SetValue(self.default_text)
            self.SetForegroundColour(wx.LIGHT_GREY)
        if event:
            event.Skip()


class AllOrMultiChoiceDialog(wx.Dialog):
    def __init__(self, parent, message, caption, choices=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        if choices is None:
            choices = []
        self.SetTitle(caption)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.message = wx.StaticText(self, -1, message)
        self.clb = wx.CheckListBox(self, -1, choices=choices)
        self.checkbox = wx.CheckBox(self, -1, 'Select all')
        self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_CHECKBOX, self.check_all, self.checkbox)

        sizer.Add(self.message, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.clb, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.checkbox, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.btns, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizerAndFit(sizer)

    def get_selections(self):
        return self.clb.GetCheckedItems()

    def check_all(self, event):
        state = self.checkbox.IsChecked()
        for i in range(self.clb.GetCount()):
            self.clb.Check(i, state)


class AdvancedEditGuide(wx.Frame):
    def __init__(self, parent):
        self.dirname = ''
        self.software_info = parent.software_info
        self.workflow_name = parent.workflow_name

        wx.Frame.__init__(self, parent, title='{} Edit Guide'.format(self.software_info.name))

        setup_frame(self, status_bar=True)

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
        self.title.SetForegroundColour(
            (self.title_contrast, self.title_contrast, self.title_contrast))  # change font color to (r,g,b)
        self.vbox_inner.Add(self.title)

        self.vbox_inner.AddSpacer(5)

        self.hbox_description = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_description.AddSpacer(5)
        self.description = wx.StaticText(self.container, label=self.software_info.advanced_edit_guide_description)
        config_status_and_tooltip(self, self.description, 'Feel free to use any capitalization scheme')
        self.hbox_description.Add(self.description)
        self.vbox_inner.Add(self.hbox_description)

        self.vbox_inner.AddSpacer(20)

        # add commands title
        self.command_title = wx.StaticText(self.container, label='Commands')
        self.command_title.SetFont(wx.Font(wx.FontInfo(14)))  # change font size
        self.command_title_contrast = self.title_contrast
        self.command_title.SetForegroundColour(
            (self.command_title_contrast, self.command_title_contrast,
             self.command_title_contrast))  # change font color to (r,g,b)
        self.vbox_inner.Add(self.command_title)

        self.nmSizer = wx.StaticBoxSizer(wx.StaticBox(self.container, -1, ''), wx.VERTICAL)
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
            config_status_and_tooltip(self, self.command, description, tooltip=False)
            self.nmSizer.Add(self.command)
            self.nmSizer.AddSpacer(5)
            if isinstance(example, list):
                for each_example in example:
                    self.example = wx.StaticText(self.container, label='   {}'.format(each_example))
                    self.example.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))  # change font size
                    self.example_contrast = 80
                    self.example.SetForegroundColour(
                        (self.example_contrast, self.example_contrast,
                         self.example_contrast))  # change font color to (r,g,b)
                    config_status_and_tooltip(self, self.example, description, tooltip=False)
                    self.nmSizer.Add(self.example)
            else:
                self.example = wx.StaticText(self.container, label='   {}'.format(example))
                self.example.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))  # change font size
                self.example_contrast = 80
                self.example.SetForegroundColour(
                    (self.example_contrast, self.example_contrast,
                     self.example_contrast))  # change font color to (r,g,b)
                config_status_and_tooltip(self, self.example, description, tooltip=False)
                self.nmSizer.Add(self.example)

            self.nmSizer.AddSpacer(15)

        self.vbox_inner.Add(self.nmSizer)

        self.vbox_inner.AddSpacer(20)

        self.docs = wx.StaticText(self.container, label='Read the Docs')
        self.docs.SetFont(wx.Font(13, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))  # change font size
        self.docs_contrast = 80
        self.docs.SetForegroundColour(
            (self.docs_contrast, self.docs_contrast,
             self.docs_contrast))  # change font color to (r,g,b)
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


class AdvancedEdit(wx.Frame):
    def __init__(self, parent):
        self.dirname = ''
        self.software_info = parent.software_info
        self.workflow_name = parent.workflow_name

        wx.Frame.__init__(self, parent,
                          title='{} Advanced Edit - {}'.format(self.software_info.name, self.workflow_name))

        # modal = True  # to make modal but encountering weird behavior
        # if modal and not hasattr(self, '_disabler'):
        #     self._disabler = wx.WindowDisabler(self)
        # if not modal and hasattr(self, '_disabler'):
        #     del self._disabler

        setup_frame(self)

        # create sizers
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox_inner = wx.BoxSizer(wx.VERTICAL)
        self.hbox_bottom = wx.BoxSizer(wx.HORIZONTAL)

        # add encompassing panel
        self.container = wx.Panel(self)

        # add workflow title
        self.title = wx.StaticText(self.container, label='{}'.format(self.workflow_name))
        self.title.SetFont(wx.Font(wx.FontInfo(18)))  # change font size
        self.title_contrast = 60
        self.title.SetForegroundColour(
            (self.title_contrast, self.title_contrast, self.title_contrast))  # change font color to (r,g,b)
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
        self.ok_btn = wx.Button(self.container, label='OK')
        self.ok_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_ok(parent))
        self.button_array.Add(self.ok_btn)
        self.cancel_btn = wx.Button(self.container, label='Cancel')
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.button_array.Add(self.cancel_btn)
        self.hbox_bottom.Add(self.button_array, 0, wx.ALIGN_RIGHT)

        self.vbox_inner.Add(self.hbox_bottom, 0, wx.EXPAND)

        self.vbox_outer.Add(self.vbox_inner, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.ALL, 10)

        self.container.SetSizer(self.vbox_outer)
        self.vbox_outer.SetSizeHints(self)

        self.Show()

    def advanced_edit_guide(self, event):
        AdvancedEditGuide(self)

    def on_cancel(self, event):
        self.Close()

    def on_ok(self, parent):
        # print(self.text_edit.GetValue() != ''.join(parent.lines))
        if self.text_edit.GetValue() != ''.join(parent.lines):
            parent.lines = ['{}\n'.format(x) for x in self.text_edit.GetValue().split('\n')]

            # write to workflow file
            with open(parent.workflow_path_name, 'w') as record_file:
                for line in parent.lines:
                    record_file.write(line)

            parent.create_edit_panel()

        self.Close()


class EditFrame(wx.Frame):
    def __init__(self, parent):
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

        wx.Frame.__init__(self, parent, title='{} Edit - {}'.format(self.software_info.name, self.workflow_name))

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
        self.back_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_back(parent))
        config_status_and_tooltip(self, self.back_btn, 'Back to workflow selection')
        self.hbox_top.Add(self.back_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        self.hbox_top.AddSpacer(10)

        # add workflow title
        self.title = wx.StaticText(self, label='{}'.format(self.workflow_name))
        self.title.SetFont(wx.Font(wx.FontInfo(18)))  # change font size
        self.title_contrast = 60
        self.title.SetForegroundColour(
            (self.title_contrast, self.title_contrast, self.title_contrast))  # change font color to (r,g,b)
        self.hbox_top.Add(self.title, 1, wx.ALIGN_CENTER_VERTICAL)

        self.vbox_outer.Add(self.hbox_top)

        self.vbox_outer.AddSpacer(10)

        # ------------------------------------------------------------------------------------------- bottom sizer

        self.hbox_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.fg_bottom = wx.FlexGridSizer(1, 2, 10, 10)

        # add edit panel
        self.edit = wx.lib.scrolledpanel.ScrolledPanel(self, style=wx.SIMPLE_BORDER, size=(500, 300))

        # read or create workflow file
        try:
            with open(self.workflow_path_name, 'r') as record_file:
                self.lines = record_file.readlines()
        except FileNotFoundError:  # create file if not found
            with open(self.workflow_path_name, 'w'):
                self.lines = []

        self.create_edit_panel()

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

        # add advanced command button
        self.advanced_btn = wx.Button(self, label='Advanced')
        self.advanced_btn.Bind(wx.EVT_BUTTON, lambda event: self.create_advanced_edit_frame())
        config_status_and_tooltip(self, self.advanced_btn, 'Advanced text-based editor')
        self.vbox_action.Add(self.advanced_btn, 0, wx.EXPAND)

        self.vbox_action.AddStretchSpacer()

        # add record command button
        self.record_btn = wx.Button(self, label='Record')
        # self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_back(parent))
        config_status_and_tooltip(self, self.record_btn, 'Record workflow actions')
        self.vbox_action.Add(self.record_btn, 0, wx.EXPAND)

        self.vbox_action.AddSpacer(10)

        # add execute command button
        self.execute_btn = wx.Button(self, label='Execute')
        # self.plus_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_back(parent))
        config_status_and_tooltip(self, self.execute_btn, 'Execute workflow actions')
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

    def create_edit_panel(self):
        for child in self.edit.GetChildren():
            child.Destroy()
        self.edit.SetupScrolling()
        self.vbox_edit = wx.BoxSizer(wx.VERTICAL)
        self.edit.SetSizer(self.vbox_edit)

        # print('lines: {}'.format(self.lines))

        self.edit.Hide()

        for index, self.line in enumerate(self.lines):
            self.hbox_edit = wx.BoxSizer(wx.HORIZONTAL)
            self.line = self.line.replace('\n', '').lower()
            if '#' in self.line or self.line == '':  # workflow comment so no action
                pass
            else:
                try:
                    self.vbox_edit.AddSpacer(5)
                    self.hbox_edit = wx.BoxSizer(wx.HORIZONTAL)
                    self.hbox_edit.AddSpacer(5)

                    self.move_up = wx.Button(self.edit, size=wx.Size(25, -1), label='▲')
                    self.move_up.Bind(wx.EVT_BUTTON, lambda event, index_trap=index: self.move_command_up(index_trap))
                    self.hbox_edit.Add(self.move_up, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.move_down = wx.Button(self.edit, size=wx.Size(25, -1), label='▼')
                    self.move_down.Bind(wx.EVT_BUTTON,
                                        lambda event, index_trap=index: self.move_command_down(index_trap))
                    self.hbox_edit.Add(self.move_down, 0, wx.ALIGN_CENTER_VERTICAL)

                    self.hbox_edit.AddSpacer(5)
                    self.line_first_word = self.line.split(' ')[0]
                    if '-mouse' in self.line_first_word:
                        self.command = wx.ComboBox(self.edit, value='Mouse button', choices=self.commands,
                                                   style=wx.CB_READONLY)
                        # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                        self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

                        if 'left' in self.line_first_word:
                            self.mouse_button = wx.ComboBox(self.edit, value='Left', choices=self.mouse_buttons,
                                                            style=wx.CB_READONLY)
                        elif 'right' in self.line_first_word:
                            self.mouse_button = wx.ComboBox(self.edit, value='Right', choices=self.mouse_buttons,
                                                            style=wx.CB_READONLY)
                        else:
                            raise CustomError('Mouse button not specified.')
                        self.hbox_edit.AddSpacer(10)
                        self.mouse_button.Bind(wx.EVT_MOUSEWHEEL,
                                               do_nothing)  # prevent mouse wheel from cycling through options
                        self.hbox_edit.Add(self.mouse_button, 0, wx.ALIGN_CENTER_VERTICAL)

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
                        self.mouse_action.Bind(wx.EVT_MOUSEWHEEL,
                                               do_nothing)  # prevent mouse wheel from cycling through options
                        self.hbox_edit.Add(self.mouse_action, 0, wx.ALIGN_CENTER_VERTICAL)

                        self.hbox_edit.AddSpacer(10)
                        self.label = wx.StaticText(self.edit, label='at pt. (  ')
                        self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                        self.x_coord = None  # redefined in self.create_point_input(self.line) method
                        self.y_coord = None  # redefined in self.create_point_input(self.line) method
                        self.create_point_input(self.line)

                    elif 'type:' in self.line_first_word:
                        self.command = wx.ComboBox(self.edit, value='Type', choices=self.commands, style=wx.CB_READONLY)
                        # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                        self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)
                        self.hbox_edit.AddSpacer(10)
                        self.text_to_type = wx.TextCtrl(self.edit, value=str(
                            self.line.replace('type: ', '').replace('Type: ', '')))
                        self.hbox_edit.Add(self.text_to_type, 0, wx.ALIGN_CENTER_VERTICAL)
                        # self.hbox_edit.Add(self.text_to_type, 1, wx.EXPAND)

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

                        # print(self.combination)

                        self.hbox_edit.AddSpacer(10)

                        self.counter = 0
                        for self.key in self.combination:
                            self.counter += 1

                            self.hotkey_cb = wx.ComboBox(self.edit, value=str(self.key), choices=self.all_keys,
                                                         style=wx.CB_READONLY)
                            self.hotkey_cb.Bind(wx.EVT_MOUSEWHEEL,
                                                do_nothing)  # prevent mouse wheel from cycling through options
                            self.hbox_edit.Add(self.hotkey_cb, 0, wx.ALIGN_CENTER_VERTICAL)

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
                            raise CustomError()

                    elif ('mouse' in self.line_first_word) and ('move' in self.line_first_word):
                        self.command = wx.ComboBox(self.edit, value='Mouse-move', choices=self.commands,
                                                   style=wx.CB_READONLY)
                        # self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
                        self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

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
                        self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

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
                        self.hbox_edit.Add(self.command, 0, wx.ALIGN_CENTER_VERTICAL)

                        self.hbox_edit.AddSpacer(10)
                        self.label = wx.StaticText(self.edit, label='at pt. (  ')
                        self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

                        self.x_coord = None  # redefined in self.create_point_input(self.line) method
                        self.y_coord = None  # redefined in self.create_point_input(self.line) method
                        self.create_point_input(self.line)

                    else:
                        raise CustomError()

                    self.command.Bind(wx.EVT_MOUSEWHEEL, do_nothing)  # prevent mouse wheel from cycling through options

                except (IndexError, CustomError) as e:
                    # print(e)
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
                self.vbox_edit.AddSpacer(5)
                self.vbox_edit.Add(wx.StaticLine(self.edit, -1), 0, wx.EXPAND)

        self.edit.Show()
        # self.edit.Update()  # no sure why this produces artifacts
        # self.Update()  # no sure why this produces artifacts

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

        self.key.Bind(wx.EVT_MOUSEWHEEL, do_nothing)  # prevent mouse wheel from cycling through options

        self.hbox_edit.Add(self.key, 0, wx.ALIGN_CENTER_VERTICAL)

    def create_point_input(self, line):
        self.x_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE, size=wx.Size(self.coord_width, -1),
                                   value=str(coords_of(line)[0]))  # TODO validator
        self.hbox_edit.Add(self.x_coord, 0, wx.ALIGN_CENTER_VERTICAL)

        self.label = wx.StaticText(self.edit, label=' , ')
        self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

        self.y_coord = wx.TextCtrl(self.edit, style=wx.TE_CENTRE, size=wx.Size(self.coord_width, -1),
                                   value=str(coords_of(line)[1]))  # , validator_float)
        self.hbox_edit.Add(self.y_coord, 0, wx.ALIGN_CENTER_VERTICAL)

        self.label = wx.StaticText(self.edit, label='  )')
        self.hbox_edit.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL)

    def on_open_delete_command_dialog(self):
        dlg = AllOrMultiChoiceDialog(self, 'Please choose the commands to delete:',
                                     '{}: {} - Delete Commands'.format(self.software_info.name, self.workflow_name),
                                     self.lines)

        if dlg.ShowModal() == wx.ID_OK:
            indices_to_delete = dlg.get_selections()
            # print('You chose to delete indices' + str(indices_to_delete))
            if indices_to_delete:  # if indices_to_delete is not empty
                for index in sorted(indices_to_delete, reverse=True):
                    del (self.lines[index])

                # write to workflow file
                with open(self.workflow_path_name, 'w') as record_file:
                    for line in self.lines:
                        record_file.write(line)

                self.create_edit_panel()

        dlg.Destroy()

    def on_open_add_command_dialog(self):
        pass
        # self.create_edit_panel()

    def create_advanced_edit_frame(self):
        AdvancedEdit(self)

    def move_command_up(self, index):
        print('Move up line {}'.format(index))
        if index > 0:
            self.lines[index - 1], self.lines[index] = self.lines[index], self.lines[index - 1]
            print(self.lines)
            self.create_edit_panel()

    def move_command_down(self, index):
        print('Move down line {}'.format(index))
        # print(len(self.lines))
        try:
            self.lines[index], self.lines[index + 1] = self.lines[index + 1], self.lines[index]
            print(self.lines)
            self.create_edit_panel()
        except IndexError:
            pass


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
        png = wx.Image('logo.png', wx.BITMAP_TYPE_PNG).Scale(150, 150, wx.IMAGE_QUALITY_BICUBIC)
        self.logo_img = wx.StaticBitmap(self.container, wx.ID_ANY, wx.Bitmap(png))
        self.vbox.Add(self.logo_img, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program name text
        self.program_name = wx.StaticText(self.container, label='{} Automation'.format(self.software_info.name))
        self.program_name.SetFont(wx.Font(wx.FontInfo(18)))  # change font
        self.program_name_contrast = 60
        self.program_name.SetForegroundColour((self.program_name_contrast, self.program_name_contrast,
                                               self.program_name_contrast))  # change font color to (r,g,b)
        self.vbox.Add(self.program_name, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program version text
        self.program_version = wx.StaticText(self.container, label='Version {}'.format(self.software_info.version))
        self.program_version.SetFont(wx.Font(wx.FontInfo(10)).Italic())  # change font
        self.program_version_contrast = 150
        self.program_version.SetForegroundColour((self.program_version_contrast, self.program_version_contrast,
                                                  self.program_version_contrast))  # change font color to (r,g,b)
        self.vbox.Add(self.program_version, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.AddSpacer(self.padding_y)

        # add input field for the workflow name
        self.workflow_name_input = PlaceholderTextCtrl(self.container, -1, placeholder='Workflow', size=(200, -1),
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
        self.cancel_btn = wx.Button(self.container, label='Quit')
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_exit)
        self.button_array.Add(self.cancel_btn)
        self.ok_btn = wx.Button(self.container, label='OK')
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        self.button_array.Add(self.ok_btn)
        self.vbox_outer.Add(self.button_array, 0, wx.ALIGN_RIGHT)

        # add south margin
        self.vbox_outer.AddSpacer(5)

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
