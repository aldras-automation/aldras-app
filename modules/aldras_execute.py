"""Aldras module containing execution objects"""
import wx
from modules.aldras_core import PlaceholderTextCtrl
from modules.aldras_settings import import_settings


def create_execute_options(parent_frame, settings_frame=False):
    def checkbox_pause_pressed():
        if not settings_frame:
            parent_frame.execute_pause_input.Enable(parent_frame.checkbox_pause.GetValue())

    def checkbox_mouse_dur_pressed():
        if not settings_frame:
            parent_frame.execute_mouse_dur_input.Enable(parent_frame.checkbox_mouse_dur.GetValue())

    def checkbox_type_interval_pressed():
        if not settings_frame:
            parent_frame.execute_type_interval_input.Enable(parent_frame.checkbox_type_interval.GetValue())

    def textctrl(placeholder_val, name):
        # TODO implement numeric validator
        if settings_frame:
            return wx.TextCtrl(parent_frame, wx.ID_ANY, value=str(placeholder_val), size=wx.Size(50, -1), style=wx.TE_CENTER, name=name)
        else:
            return PlaceholderTextCtrl(parent_frame, wx.ID_ANY, placeholder=str(placeholder_val), size=wx.Size(50, -1), style=wx.TE_CENTER, name=name)

    settings = import_settings()

    vbox = wx.BoxSizer(wx.VERTICAL)
    vbox.AddSpacer(10)

    # execution pause input
    hbox_pause = wx.BoxSizer(wx.HORIZONTAL)  # --------------------------------------------------------

    parent_frame.checkbox_pause = wx.CheckBox(parent_frame, label=' Pause between commands: ', name='Execute pause between commands checked')
    parent_frame.checkbox_pause.SetValue(settings['Execute pause between commands checked'])
    parent_frame.checkbox_pause.Bind(wx.EVT_CHECKBOX, lambda event: checkbox_pause_pressed())
    hbox_pause.Add(parent_frame.checkbox_pause, 0, wx.ALIGN_CENTER_VERTICAL)

    parent_frame.execute_pause_input = textctrl(settings['Execute pause between commands'], 'Execute pause between commands')
    hbox_pause.Add(parent_frame.execute_pause_input, 0, wx.ALIGN_CENTER_VERTICAL)

    hbox_pause.Add(wx.StaticText(parent_frame, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
    vbox.Add(hbox_pause, 0, wx.EAST | wx.WEST, 10)
    # ------------------------------------------------------------------------------------------------------

    vbox.AddSpacer(20)

    # Mouse duration input
    hbox_mouse_dur = wx.BoxSizer(wx.HORIZONTAL)  # ----------------------------------------------------

    parent_frame.checkbox_mouse_dur = wx.CheckBox(parent_frame, label=' Mouse command duration: ', name='Execute mouse command duration checked')
    parent_frame.checkbox_mouse_dur.SetValue(settings['Execute mouse command duration checked'])
    parent_frame.checkbox_mouse_dur.Bind(wx.EVT_CHECKBOX, lambda event: checkbox_mouse_dur_pressed())
    hbox_mouse_dur.Add(parent_frame.checkbox_mouse_dur, 0, wx.ALIGN_CENTER_VERTICAL)

    parent_frame.execute_mouse_dur_input = textctrl(settings['Execute mouse command duration'], 'Execute mouse command duration')
    hbox_mouse_dur.Add(parent_frame.execute_mouse_dur_input, 0, wx.ALIGN_CENTER_VERTICAL)

    hbox_mouse_dur.Add(wx.StaticText(parent_frame, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
    vbox.Add(hbox_mouse_dur, 0, wx.EAST | wx.WEST, 10)
    # ------------------------------------------------------------------------------------------------------

    vbox.AddSpacer(20)

    # Text type interval duration input
    hbox_type_interval = wx.BoxSizer(wx.HORIZONTAL)  # ------------------------------------------------

    parent_frame.checkbox_type_interval = wx.CheckBox(parent_frame, label=' Interval between text character outputs: ', name='Interval between text character outputs checked')
    parent_frame.checkbox_type_interval.SetValue(settings['Interval between text character outputs checked'])
    parent_frame.checkbox_type_interval.Bind(wx.EVT_CHECKBOX, lambda event: checkbox_type_interval_pressed())
    hbox_type_interval.Add(parent_frame.checkbox_type_interval, 0, wx.ALIGN_CENTER_VERTICAL)

    parent_frame.execute_type_interval_input = textctrl(settings['Interval between text character outputs'], 'Interval between text character outputs')
    hbox_type_interval.Add(parent_frame.execute_type_interval_input, 0, wx.ALIGN_CENTER_VERTICAL)

    hbox_type_interval.Add(wx.StaticText(parent_frame, label='  sec'), 0, wx.ALIGN_CENTER_VERTICAL)
    vbox.Add(hbox_type_interval, 0, wx.EAST | wx.WEST, 10)
    # ------------------------------------------------------------------------------------------------------

    checkbox_pause_pressed()
    checkbox_mouse_dur_pressed()
    checkbox_type_interval_pressed()

    return vbox


class ExecuteDialog(wx.Dialog):
    def __init__(self, parent, caption):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE)  # | wx.RESIZE_BORDER)
        self.SetTitle(caption)
        self.SetIcon(wx.Icon(parent.software_info.icon, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour('white')

        vbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Options'), wx.VERTICAL)

        # instantiate attributes to be redefined in create_execute_options() and used in ExecuteCtrlCounterDialog
        self.checkbox_pause = None
        self.execute_pause_input = None
        self.checkbox_mouse_dur = None
        self.execute_mouse_dur_input = None
        self.checkbox_type_interval = None
        self.execute_type_interval_input = None

        vbox.Add(create_execute_options(self))

        vbox.AddSpacer(10)

        btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)

        vbox_outer = wx.BoxSizer(wx.VERTICAL)
        vbox_outer.Add(wx.StaticText(self, label='Uncheck option(s) for fastest execution'), 0,
                            wx.ALIGN_RIGHT | wx.NORTH | wx.EAST | wx.WEST, 20)
        vbox_outer.Add(vbox, 0, wx.EAST | wx.WEST | wx.SOUTH, 20)
        vbox_outer.Add(btns, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.SOUTH, 15)
        self.SetSizerAndFit(vbox_outer)
        self.Center()