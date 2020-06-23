"""Aldras module containing execution-related code"""
import wx
from modules.aldras_core import PlaceholderTextCtrl


def create_execute_options(parent_frame):
    def checkbox_pause_pressed():
        parent_frame.execute_pause_input.Enable(parent_frame.checkbox_pause.GetValue())

    def checkbox_mouse_dur_pressed():
        parent_frame.execute_mouse_dur_input.Enable(parent_frame.checkbox_mouse_dur.GetValue())

    def checkbox_type_interval_pressed():
        parent_frame.execute_type_interval_input.Enable(parent_frame.checkbox_type_interval.GetValue())

    vbox = wx.BoxSizer(wx.VERTICAL)
    vbox.AddSpacer(10)

    # execution pause input
    parent_frame.hbox_pause = wx.BoxSizer(wx.HORIZONTAL)  # --------------------------------------------------------

    parent_frame.checkbox_pause = wx.CheckBox(parent_frame, label=' Pause between commands: ')
    parent_frame.checkbox_pause.SetValue(True)
    parent_frame.checkbox_pause.Bind(wx.EVT_CHECKBOX, lambda event: checkbox_pause_pressed())
    parent_frame.hbox_pause.Add(parent_frame.checkbox_pause, 0, wx.ALIGN_CENTER_VERTICAL)

    parent_frame.execute_pause_input = PlaceholderTextCtrl(parent_frame, wx.ID_ANY, placeholder='0.2', size=wx.Size(50, -1),
                                                   style=wx.TE_CENTER)
    parent_frame.hbox_pause.Add(parent_frame.execute_pause_input, 0, wx.ALIGN_CENTER_VERTICAL)

    parent_frame.hbox_pause.Add(wx.StaticText(parent_frame, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
    vbox.Add(parent_frame.hbox_pause, 0, wx.EAST | wx.WEST, 10)
    # ------------------------------------------------------------------------------------------------------

    vbox.AddSpacer(20)

    # Mouse duration input
    parent_frame.hbox_mouse_dur = wx.BoxSizer(wx.HORIZONTAL)  # ----------------------------------------------------

    parent_frame.checkbox_mouse_dur = wx.CheckBox(parent_frame, label=' Mouse command duration: ')
    parent_frame.checkbox_mouse_dur.SetValue(True)
    parent_frame.checkbox_mouse_dur.Bind(wx.EVT_CHECKBOX, lambda event: checkbox_mouse_dur_pressed())
    parent_frame.hbox_mouse_dur.Add(parent_frame.checkbox_mouse_dur, 0, wx.ALIGN_CENTER_VERTICAL)

    parent_frame.execute_mouse_dur_input = PlaceholderTextCtrl(parent_frame, wx.ID_ANY, placeholder='1',
                                                       size=wx.Size(50, -1),
                                                       style=wx.TE_CENTER)
    parent_frame.hbox_mouse_dur.Add(parent_frame.execute_mouse_dur_input, 0, wx.ALIGN_CENTER_VERTICAL)

    parent_frame.hbox_mouse_dur.Add(wx.StaticText(parent_frame, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
    vbox.Add(parent_frame.hbox_mouse_dur, 0, wx.EAST | wx.WEST, 10)
    # ------------------------------------------------------------------------------------------------------

    vbox.AddSpacer(20)

    # Text type interval duration input
    parent_frame.hbox_type_interval = wx.BoxSizer(wx.HORIZONTAL)  # ------------------------------------------------

    parent_frame.checkbox_type_interval = wx.CheckBox(parent_frame, label=' Interval between text character outputs: ')
    parent_frame.checkbox_type_interval.SetValue(True)
    parent_frame.checkbox_type_interval.Bind(wx.EVT_CHECKBOX, lambda event: checkbox_type_interval_pressed())
    parent_frame.hbox_type_interval.Add(parent_frame.checkbox_type_interval, 0, wx.ALIGN_CENTER_VERTICAL)

    parent_frame.execute_type_interval_input = PlaceholderTextCtrl(parent_frame, wx.ID_ANY, placeholder='0.05',
                                                           size=wx.Size(50, -1)
                                                           , style=wx.TE_CENTER)
    parent_frame.hbox_type_interval.Add(parent_frame.execute_type_interval_input, 0, wx.ALIGN_CENTER_VERTICAL)

    parent_frame.hbox_type_interval.Add(wx.StaticText(parent_frame, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
    vbox.Add(parent_frame.hbox_type_interval, 0, wx.EAST | wx.WEST, 10)
    # ------------------------------------------------------------------------------------------------------

    return vbox


class ExecuteDialog(wx.Dialog):
    def __init__(self, parent, caption):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)  # | wx.RESIZE_BORDER)
        self.parent = parent
        self.SetTitle(caption)
        self.SetIcon(wx.Icon(self.parent.software_info.icon, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour('white')

        self.vbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Options'), wx.VERTICAL)

        self.vbox.Add(create_execute_options(self))

        self.vbox.AddSpacer(10)

        self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)

        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox_outer.Add(wx.StaticText(self, label='Uncheck option(s) for fastest execution'), 0,
                            wx.ALIGN_RIGHT | wx.NORTH | wx.EAST | wx.WEST, 20)
        self.vbox_outer.Add(self.vbox, 0, wx.EAST | wx.WEST | wx.SOUTH, 20)
        self.vbox_outer.Add(self.btns, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, 15)
        self.SetSizerAndFit(self.vbox_outer)
        self.Center()
