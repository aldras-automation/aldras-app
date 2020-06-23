# import images
import wx


class SettingsFrame(wx.Frame):
    """Main frame to select workflow."""

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=f'Settings', name='settings_frame')
        self.SetBackgroundColour('white')
        # self.parent = parent
        # self.SetIcon(wx.Icon(self.parent.software_info.icon, wx.BITMAP_TYPE_ICO))  # assign icon
        # self.Bind(wx.EVT_CLOSE, self.close_window)

        padding = 5
        margin = 40

        static_boxsizer_inner_padding = 10
        static_boxsizer_outer_spacing = 20


        # create sizers
        vbox_outer = wx.BoxSizer(wx.VERTICAL)
        vbox_container = wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)
        panel.SetSizer(vbox_container)

        general_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'General'), wx.VERTICAL)  # -------------------

        num_recent_workflows_hbox = wx.BoxSizer(wx.HORIZONTAL)

        num_recent_workflows_st = wx.StaticText(panel, label='Number of recent workflows displayed:')
        num_recent_workflows_hbox.Add(num_recent_workflows_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        num_recent_workflows_cb = wx.ComboBox(panel, value='3', choices=[str(ii) for ii in range(1, 6)], style=wx.CB_READONLY)
        num_recent_workflows_hbox.Add(num_recent_workflows_cb, 0, wx.ALIGN_CENTER_VERTICAL)

        general_sizer.Add(num_recent_workflows_hbox, 0, wx.ALL, static_boxsizer_inner_padding)
        vbox_container.Add(general_sizer, 0, wx.EXPAND | wx.SOUTH, static_boxsizer_outer_spacing)  # -------------------

        #

        mouse_monitor_sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Mouse Monitor'), wx.VERTICAL)  # -------

        mouse_monitor_freeze_mthd_hbox = wx.BoxSizer(wx.HORIZONTAL)

        mouse_monitor_freeze_mthd_st = wx.StaticText(panel, label='Default freeze method:')
        mouse_monitor_freeze_mthd_hbox.Add(mouse_monitor_freeze_mthd_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        mouse_monitor_freeze_mthd_cb = wx.ComboBox(panel, value='Click or Ctrl', choices=['None', 'Click', 'Ctrl', 'Click or Ctrl'], style=wx.CB_READONLY)
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
        # vbox_live.SetMinSize(vbox_live.GetSize())  # prevent resizing of window as length of live coordinate changes

        self.Center()
        self.Show()

    def close_window(self, close_event):
        close_event.Skip()


########################################################################
class TabPanel(wx.Panel):
    """
    This will be the first notebook tab
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
        txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txtOne, 0, wx.ALL, 5)
        sizer.Add(txtTwo, 0, wx.ALL, 5)

        self.SetSizer(sizer)


########################################################################
class NotebookDemo(wx.Notebook):
    """
    Notebook class
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
        wx.BK_DEFAULT
                             # wx.BK_TOP
                             # wx.BK_BOTTOM
                             # wx.BK_LEFT
                             # wx.BK_RIGHT
                             )

        tab_general = wx.Panel(self)
        self.AddPage(tab_general, 'General')

        vbox_general = wx.BoxSizer(wx.VERTICAL)

        # num_recent_workflows_hbox = wx.BoxSizer(wx.HORIZONTAL)
        num_recent_workflows_hbox = wx.StaticBoxSizer(wx.StaticBox(tab_general, wx.ID_ANY, 'General'), wx.HORIZONTAL)

        num_recent_workflows_st = wx.StaticText(tab_general, label='Number of recent workflows displayed:')
        num_recent_workflows_hbox.Add(num_recent_workflows_st, 0, wx.ALIGN_CENTER_VERTICAL | wx.EAST, 10)

        num_recent_workflows_cb = wx.ComboBox(tab_general, value='3', choices=[str(ii) for ii in range(1,6)])
        num_recent_workflows_hbox.Add(num_recent_workflows_cb, 0, wx.ALIGN_CENTER_VERTICAL)

        vbox_general.Add(num_recent_workflows_hbox)


        st2 = wx.StaticText(tab_general, label='Test for thing2:')
        vbox_general.Add(st2)

        tab_general.SetSizer(vbox_general)

        # Create and add the second tab
        tabTwo = TabPanel(self)
        self.AddPage(tabTwo, "TabTwo")

        # Create and add the third tab
        self.AddPage(TabPanel(self), "TabThree")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # print
        # 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # print
        # 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()


########################################################################
class DemoFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Notebook Tutorial",
                          size=(600, 400)
                          )
        panel = wx.Panel(self)

        notebook = NotebookDemo(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()

        self.Show()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = SettingsFrame(None)
    app.MainLoop()