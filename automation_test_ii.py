import wx


########################################################################
class MyForm(wx.Frame):

    # ----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Tutorial")
        panel = wx.Panel(self, wx.ID_ANY)

        self.ct = 0
        self.phaseSelection = ""
        self.opSelection = ""
        self.instSelection = ""
        self.orgSelection = ""

        phasesList = ["preOperations", "inOperations", "postOperations"]

        self.combo = wx.ComboBox(panel, choices=phasesList)
        self.combo.Bind(wx.EVT_COMBOBOX, self.onCombo)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.combo)
        panel.SetSizer(sizer)

    # ----------------------------------------------------------------------
    def onCombo(self, event):
        """
        """
        self.phaseSelection = self.combo.GetValue()
        print(self.phaseSelection)


# ----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm().Show()
    app.MainLoop()
