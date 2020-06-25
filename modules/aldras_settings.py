"""Aldras module containing settings objects"""
import wx
import json

settings_possibilities = {
    'Number of recent workflows displayed': [str(ii) for ii in list(range(0, 6))],  # one to five
    'Freeze method': ['None', 'Click', 'Ctrl', 'Click or ctrl'],
    'Record pause': ['No pauses', 'All pauses', 'Pauses over'],
    'Record method': ['Overwrite', 'Append'],
}


def validate_settings(settings_unvalidated):
    # factory settings for reference comparison (double quotes used rather than single quote convention due to desire to allow copy-paste between this dictionary and the .json file)
    factory_settings = {
        "Number of recent workflows displayed": 3,
        "Freeze method": "Click or Ctrl",
        "Record pause": "No pauses",
        "Record pause over duration": 0.2,
        "Record method": "Overwrite",
        "Execute pause between commands": 0.2,
        "Execute pause between commands checked": "True",
        "Execute mouse command duration": 0.5,
        "Execute mouse command duration checked": "True",
        "Interval between text character outputs": 0.05,
        "Interval between text character outputs checked": "True"
    }

    # settings validation lambda functions
    settings_validation = {
        'Number of recent workflows displayed': lambda x: str(x) in settings_possibilities[
            'Number of recent workflows displayed'],
        'Freeze method': lambda x: x.lower() in [y.lower() for y in settings_possibilities['Freeze method']],
        'Record pause': lambda x: x.lower() in [y.lower() for y in settings_possibilities['Record pause']],
        'Record pause over duration': lambda x: x > 0,
        'Record method': lambda x: x.lower() in [y.lower() for y in settings_possibilities['Record method']],
        'Execute pause between commands': lambda x: x > 0,
        'Execute pause between commands checked': lambda x: x in [True, False],
        'Execute mouse command duration': lambda x: x > 0,
        'Execute mouse command duration checked': lambda x: x in [True, False],
        'Interval between text character outputs': lambda x: x > 0,
        'Interval between text character outputs checked': lambda x: x in [True, False]
    }

    settings = dict()
    for key in factory_settings:  # loop through the factory settings and attempt to parse imported setting if available

        # determine type of factory settings to cast imported settings
        if factory_settings[key] in ['True', 'False']:
            cast_type = bool
        else:
            cast_type = type(factory_settings[key])

        try:
            if settings_validation[key](
                    cast_type(settings_unvalidated[key])):  # if the cast imported setting is validated
                settings[key] = cast_type(settings_unvalidated[key])  # set equal to the cast imported setting

                if isinstance(settings[key], str):
                    settings[key] = settings[key].capitalize()  # capitalize setting if string
            else:
                raise ValueError
        except (KeyError, ValueError):
            settings[key] = cast_type(factory_settings[key])

    return settings


def import_settings():
    # open data/settings.json file to import settings, otherwise create empty dictionary to use factory settings
    try:
        with open('data/settings.json', 'r') as json_file:
            imported_settings = json.load(json_file)

    except (FileNotFoundError, json.decoder.JSONDecodeError) as error:
        imported_settings = dict()

        # reconstruct settings.json file with factory settings
        with open('data/settings.json', 'w') as json_file:
            json.dump(validate_settings(dict()), json_file, indent=4)

        if isinstance(error, FileNotFoundError):
            wx.MessageDialog(None, 'The \'settings.json\' file could not be located and has been reconstructed.',
                             'Missing settings.json file', wx.OK | wx.ICON_INFORMATION).ShowModal()
        if isinstance(error, json.decoder.JSONDecodeError):
            wx.MessageDialog(None, 'The \'settings.json\' file could not be decoded and has been reconstructed.',
                             'Corrupt settings.json file', wx.OK | wx.ICON_INFORMATION).ShowModal()

    return validate_settings(imported_settings)


def save_settings(settings):
    settings = validate_settings(settings)
    with open('data/settings.json', 'w') as json_file:
        json.dump(settings, json_file, indent=4)


class SettingsDialog(wx.Dialog):
    """Main frame to select workflow."""

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=f'Settings', name='settings_frame')
        self.SetBackgroundColour('white')
        if parent:
            self.SetIcon(wx.Icon(parent.software_info.icon, wx.BITMAP_TYPE_ICO))  # assign icon

        margin = 30

        def setting_cb(parameter):
            return wx.ComboBox(panel, value=str(self.settings[parameter]), choices=settings_possibilities[parameter],
                               style=wx.CB_READONLY)

        self.settings = import_settings()
        self.settings_as_imported = self.settings.copy()

        static_boxsizer_inner_padding = 10
        static_boxsizer_outer_spacing = 20

        # create sizers
        vbox_outer = wx.BoxSizer(wx.VERTICAL)
        vbox_main = wx.BoxSizer(wx.VERTICAL)
        vbox_container = wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)

        selection_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Workflow Selection'), wx.VERTICAL)  # ------

        num_recent_workflows_hbox = wx.BoxSizer(wx.HORIZONTAL)

        num_recent_workflows_st = wx.StaticText(panel, label='Number of recent workflows displayed:')
        num_recent_workflows_hbox.Add(num_recent_workflows_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        num_recent_workflows_cb = setting_cb('Number of recent workflows displayed')
        num_recent_workflows_cb.Bind(wx.EVT_COMBOBOX, lambda event: self.setting_change(event.GetString(),
                                                                                        'Number of recent workflows displayed'))
        num_recent_workflows_hbox.Add(num_recent_workflows_cb, 0, wx.ALIGN_CENTER_VERTICAL)

        selection_sizer.Add(num_recent_workflows_hbox, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(selection_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # -----------------

        #

        mouse_monitor_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Mouse Monitor'), wx.VERTICAL)  # -------

        mouse_monitor_freeze_mthd_hbox = wx.BoxSizer(wx.HORIZONTAL)

        mouse_monitor_freeze_mthd_st = wx.StaticText(panel, label='Freeze method:')
        mouse_monitor_freeze_mthd_hbox.Add(mouse_monitor_freeze_mthd_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        mouse_monitor_freeze_mthd_cb = setting_cb('Freeze method')
        mouse_monitor_freeze_mthd_cb.Bind(wx.EVT_COMBOBOX,
                                          lambda event: self.setting_change(event.GetString(), 'Freeze method'))
        mouse_monitor_freeze_mthd_hbox.Add(mouse_monitor_freeze_mthd_cb, 0, wx.ALIGN_CENTER_VERTICAL)

        mouse_monitor_sizer.Add(mouse_monitor_freeze_mthd_hbox, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(mouse_monitor_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # -------------

        #

        record_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Record Options'), wx.VERTICAL)  # -------------

        from modules.aldras_record import create_record_options
        record_options_sizer = create_record_options(panel, settings_frame=True)

        # bind parameter changes to setting_change()
        for record_pause_option in settings_possibilities['Record pause']:
            self.FindWindowByLabel(record_pause_option).Bind(wx.EVT_RADIOBUTTON, lambda event: self.setting_change(
                event.GetEventObject().GetLabel(), 'Record pause'))

        self.FindWindowByLabel(self.settings['Record pause']).SetValue(True)

        self.FindWindowByName('some_sleep_thresh').SetValue(str(self.settings['Record pause over duration']))
        self.FindWindowByName('some_sleep_thresh').Bind(wx.EVT_TEXT, lambda event: self.setting_change(
            event.GetEventObject().GetValue(), 'Record pause over duration'))

        self.FindWindowByName('Record method').SetSelection(
            self.FindWindowByName('Record method').FindString(self.settings['Record method']))
        self.FindWindowByName('Record method').Bind(wx.EVT_RADIOBOX, lambda event: self.setting_change(
            event.GetEventObject().GetString(event.GetEventObject().GetSelection()), 'Record method'))

        record_sizer.Add(record_options_sizer, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(record_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # --------------------

        #

        execute_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Execute Options'), wx.VERTICAL)  # -----------

        from modules.aldras_execute import create_execute_options
        execute_options_sizer = create_execute_options(panel, settings_frame=True)

        for setting_name in ['Execute pause between commands', 'Execute pause between commands checked',
                             'Execute mouse command duration', 'Execute mouse command duration checked',
                             'Interval between text character outputs',
                             'Interval between text character outputs checked']:
            widget = self.FindWindowByName(setting_name)

            if isinstance(widget, wx.CheckBox):  # set true or false, not string
                widget.SetValue(self.settings[setting_name])
                widget.Bind(wx.EVT_CHECKBOX,
                            lambda event, setting=setting_name: self.setting_change(event.GetEventObject().GetValue(),
                                                                                    setting))
            elif isinstance(widget, wx.TextCtrl):
                widget.SetValue(str(self.settings[setting_name]))
                widget.Bind(wx.EVT_TEXT,
                            lambda event, setting=setting_name: self.setting_change(event.GetEventObject().GetValue(),
                                                                                    setting))

        execute_sizer.Add(execute_options_sizer, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(execute_sizer, 0, wx.EXPAND)  # -------------------------------------------------------------

        panel.SetSizer(vbox_container)
        vbox_main.Add(panel, 0, wx.EXPAND | wx.SOUTH, 20)

        # add buttons
        btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        vbox_main.Add(btns, 0, wx.EXPAND | wx.ALL, 5)

        self.FindWindowById(wx.ID_OK).Enable(False)

        vbox_outer.AddStretchSpacer()
        vbox_outer.Add(vbox_main, 0, wx.EXPAND | wx.NORTH | wx.WEST | wx.EAST, margin)
        vbox_outer.AddSpacer(margin / 2)
        vbox_outer.AddStretchSpacer()

        self.SetSizerAndFit(vbox_outer)

        self.Center()

    def setting_change(self, value, setting):
        self.settings[setting] = value
        self.settings = validate_settings(self.settings)

        if self.settings != self.settings_as_imported:
            self.FindWindowById(wx.ID_OK).Enable()  # enable OK button if changes
        else:
            self.FindWindowById(wx.ID_OK).Enable(False)  # disable OK button if no changes