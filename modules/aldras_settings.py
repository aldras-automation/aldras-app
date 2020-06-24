"""Aldras module containing SettingsFrame"""
import wx


class SettingsFrame(wx.Dialog):
    """Main frame to select workflow."""

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=f'Settings', name='settings_frame')
        self.SetBackgroundColour('white')
        if parent:
            self.SetIcon(wx.Icon(parent.software_info.icon, wx.BITMAP_TYPE_ICO))  # assign icon
        # self.Bind(wx.EVT_CLOSE, self.close_window)

        margin = 30

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

        num_recent_workflows_cb = wx.ComboBox(panel, value='3', choices=[str(ii) for ii in range(1, 6)], style=wx.CB_READONLY)
        num_recent_workflows_hbox.Add(num_recent_workflows_cb, 0, wx.ALIGN_CENTER_VERTICAL)

        selection_sizer.Add(num_recent_workflows_hbox, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(selection_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # -----------------

        #

        mouse_monitor_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Mouse Monitor'), wx.VERTICAL)  # -------

        mouse_monitor_freeze_mthd_hbox = wx.BoxSizer(wx.HORIZONTAL)

        mouse_monitor_freeze_mthd_st = wx.StaticText(panel, label='Default freeze method:')
        mouse_monitor_freeze_mthd_hbox.Add(mouse_monitor_freeze_mthd_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        mouse_monitor_freeze_mthd_cb = wx.ComboBox(panel, value='Click or ctrl', choices=['None', 'Click', 'Ctrl', 'Click or ctrl'], style=wx.CB_READONLY)
        mouse_monitor_freeze_mthd_hbox.Add(mouse_monitor_freeze_mthd_cb, 0, wx.ALIGN_CENTER_VERTICAL)

        mouse_monitor_sizer.Add(mouse_monitor_freeze_mthd_hbox, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(mouse_monitor_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # -------------

        #

        record_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Default Record Options'), wx.VERTICAL)  # -----

        from modules.aldras_record import create_record_options
        record_options_sizer = create_record_options(panel)

        record_sizer.Add(record_options_sizer, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(record_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # --------------------

        #

        execute_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Default Execute Options'), wx.VERTICAL)  # ---

        from modules.aldras_execute import create_execute_options
        execute_options_sizer = create_execute_options(panel)

        execute_sizer.Add(execute_options_sizer, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(execute_sizer, 0, wx.EXPAND)  # --------------------------------------------------------------

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