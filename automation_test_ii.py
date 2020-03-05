import wx
import wx.lib.scrolledpanel as scrolled


########################################################################
class MyForm(wx.Frame):

    # ----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Tutorial", size=(200, 500))

        # Add a panel so it looks the correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)

        # --------------------
        # Scrolled panel stuff
        self.edit = scrolled.ScrolledPanel(self.panel, -1,
                                           style=wx.TAB_TRAVERSAL)
        self.edit.SetAutoLayout(1)
        self.edit.SetupScrolling()

        self.vbox_edit = wx.BoxSizer(wx.VERTICAL)

        for ii in range(20):
            self.vbox_edit.Add(wx.Button(self.edit, label='OK'))
        self.edit.SetSizer(self.vbox_edit)
        # --------------------

        # btn = wx.Button(self.panel, label="Add Widget")
        # btn.Bind(wx.EVT_BUTTON, self.onAdd)

        panelSizer = wx.BoxSizer(wx.VERTICAL)
        # panelSizer.AddSpacer(50)
        panelSizer.Add(self.edit, 1, wx.EXPAND)
        # panelSizer.Add(btn)
        self.panel.SetSizer(panelSizer)

    # ----------------------------------------------------------------------
    def onAdd(self, event):
        """"""
        print
        "in onAdd"
        new_text = wx.TextCtrl(self.edit, value="New Text")
        self.spSizer.Add(new_text)
        self.edit.Layout()
        self.edit.SetupScrolling()


# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm().Show()
    app.MainLoop()
