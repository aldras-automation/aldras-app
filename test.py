import wx

class LicenseFrame(wx.Frame):
    """Main frame to select workflow."""

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='License stuff')
        self.license_input = wx.TextCtrl(self, wx.ID_ANY, size=(200, -1))

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.license_input, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox_outer.AddStretchSpacer()
        self.vbox_outer.Add(self.vbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
        self.vbox_outer.AddStretchSpacer()

        # add buttons
        self.button_array = wx.StdDialogButtonSizer()
        self.activate_btn = wx.Button(self, label='Activate')
        self.activate_btn.Bind(wx.EVT_BUTTON, self.on_activate)
        self.button_array.Add(self.activate_btn)
        self.button_array.AddSpacer(5)
        self.verify_btn = wx.Button(self, label='Verify')
        self.verify_btn.Bind(wx.EVT_BUTTON, self.on_verify)
        self.button_array.Add(self.verify_btn)
        self.vbox_outer.Add(self.button_array, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        # self.vbox_outer.SetSizeHints(self)

        self.SetSizer(self.vbox_outer)
        self.Center()
        self.Show()

    def on_activate(self, _):
        LicenseFrame(None)

    def on_verify(self, _):
        wx.MessageDialog(self, 'Idk', 'Activation', wx.OK | wx.ICON_INFORMATION).ShowModal()


app = wx.App(False)
LicenseFrame(None)
app.MainLoop()
