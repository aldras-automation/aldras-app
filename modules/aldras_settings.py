"""Aldras module containing SettingsFrame"""
import wx
import json


settings_possibilities = {
    'Number of recent workflows displayed': [str(ii) for ii in list(range(0, 6))],  # one to five
    'Freeze method': ['None', 'Click', 'Ctrl', 'Click or ctrl'],
    'Record pause': ['No pauses', 'All pauses', 'Pauses over'],
    'Record method': ['Overwrite', 'Append'],
}


def import_settings():
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
        'Number of recent workflows displayed': lambda x: str(x) in settings_possibilities['Number of recent workflows displayed'],
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

    # open data/settings.json file to import settings, otherwise create empty dictionary to use factory settings
    try:
        with open('../data/settings.json', 'r') as file:
            imported_settings = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        imported_settings = dict()
        wx.MessageDialog(None, 'The \'settings.json\' file could not be located and was recreated.', 'Missing settings.json file', wx.OK | wx.ICON_INFORMATION).ShowModal()

    settings = dict()
    for key in factory_settings:  # loop through the factory settings and attempt to parse imported setting if available

        # determine type of factory settings to cast imported settings
        if factory_settings[key] in ['True', 'False']:
            cast_type = bool
        else:
            cast_type = type(factory_settings[key])

        try:
            if settings_validation[key](cast_type(imported_settings[key])):  # if the cast imported setting is validated
                settings[key] = cast_type(imported_settings[key])  # set equal to the cast imported setting

                if isinstance(settings[key], str):
                    settings[key] = settings[key].capitalize()  # capitalize setting if string
            else:
                raise ValueError
        except (KeyError, ValueError):
            print(key)
            settings[key] = cast_type(factory_settings[key])

    return settings


def export_settings(settings):
    with open('../data/settings.json', 'w') as json_file:
        json.dump(settings, json_file, indent=4)


class SettingsFrame(wx.Dialog):
    """Main frame to select workflow."""

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=f'Settings', name='settings_frame')
        self.SetBackgroundColour('white')
        if parent:
            self.SetIcon(wx.Icon(parent.software_info.icon, wx.BITMAP_TYPE_ICO))  # assign icon
        # self.Bind(wx.EVT_CLOSE, self.close_window)

        margin = 30

        def setting_cb(parameter):
            return wx.ComboBox(panel, value=str(settings[parameter]), choices=settings_possibilities[parameter], style=wx.CB_READONLY)

        settings = import_settings()

        static_boxsizer_inner_padding = 10
        static_boxsizer_outer_spacing = 20

        # create sizers
        vbox_outer = wx.BoxSizer(wx.VERTICAL)
        vbox_container = wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)
        panel.SetSizer(vbox_container)

        selection_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Workflow Selection'), wx.VERTICAL)  # ------

        num_recent_workflows_hbox = wx.BoxSizer(wx.HORIZONTAL)

        num_recent_workflows_st = wx.StaticText(panel, label='Number of recent workflows displayed:')
        num_recent_workflows_hbox.Add(num_recent_workflows_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        num_recent_workflows_cb = setting_cb('Number of recent workflows displayed')
        num_recent_workflows_hbox.Add(num_recent_workflows_cb, 0, wx.ALIGN_CENTER_VERTICAL)

        selection_sizer.Add(num_recent_workflows_hbox, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(selection_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # -----------------

        #

        mouse_monitor_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Mouse Monitor'), wx.VERTICAL)  # -------

        mouse_monitor_freeze_mthd_hbox = wx.BoxSizer(wx.HORIZONTAL)

        mouse_monitor_freeze_mthd_st = wx.StaticText(panel, label='Freeze method:')
        mouse_monitor_freeze_mthd_hbox.Add(mouse_monitor_freeze_mthd_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        mouse_monitor_freeze_mthd_cb = setting_cb('Freeze method')
        mouse_monitor_freeze_mthd_hbox.Add(mouse_monitor_freeze_mthd_cb, 0, wx.ALIGN_CENTER_VERTICAL)

        mouse_monitor_sizer.Add(mouse_monitor_freeze_mthd_hbox, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(mouse_monitor_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # -------------

        #

        record_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Record Options'), wx.VERTICAL)  # -------------

        from modules.aldras_record import create_record_options
        record_options_sizer = create_record_options(panel, settings_frame=True)

        self.FindWindowByLabel(settings['Record pause']).SetValue(True)
        self.FindWindowByName('some_sleep_thresh').SetValue(str(settings['Record pause over duration']))

        record_sizer.Add(record_options_sizer, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(record_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # --------------------

        #

        execute_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Execute Options'), wx.VERTICAL)  # -----------

        from modules.aldras_execute import create_execute_options
        execute_options_sizer = create_execute_options(panel, settings_frame=True)

        # if settings['Execute pause between commands checked']:
        self.FindWindowByName('Execute pause between commands').SetValue(str(settings['Execute pause between commands']))
        self.FindWindowByLabel(' Pause between commands: ').SetValue(settings['Execute pause between commands checked'])

        self.FindWindowByName('Execute mouse command duration').SetValue(str(settings['Execute mouse command duration']))
        self.FindWindowByLabel(' Mouse command duration: ').SetValue(settings['Execute mouse command duration checked'])

        self.FindWindowByName('Interval between text character outputs').SetValue(str(settings['Interval between text character outputs']))
        self.FindWindowByLabel(' Interval between text character outputs: ').SetValue(settings['Interval between text character outputs checked'])

        execute_sizer.Add(execute_options_sizer, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(execute_sizer, 0, wx.EXPAND)  # -------------------------------------------------------------

        vbox_outer.AddStretchSpacer()
        vbox_outer.Add(panel, 0, wx.EXPAND | wx.ALL, margin)
        vbox_outer.AddStretchSpacer()

        self.SetSizerAndFit(vbox_outer)

        self.Center()
        self.Show()

    def close_window(self, close_event):
        close_event.Skip()


if __name__ == "__main__":  # debugging capability by running module file as main
    app = wx.App()
    frame = SettingsFrame(None)
    app.MainLoop()
