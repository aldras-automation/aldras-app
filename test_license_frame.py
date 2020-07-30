text = 50*'''
ScrolledPanel extends wx.ScrolledWindow, adding all
the necessary bits to set up scroll handling for you.

Here are three fixed size examples of its use. The
demo panel for this sample is also using it -- the
wx.StaticLine below is intentionally made too long so a scrollbar will be
activated.'''

import wx
import wx.lib.scrolledpanel as scrolled


class EULAFrame(wx.Frame):
    """Frame to display EULA"""

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='Aldras: End User License Agreement', name='eula_frame')
        self.SetBackgroundColour(wx.WHITE)
        self.SetIcon(wx.Icon('data/aldras.ico', wx.BITMAP_TYPE_ICO))  # assign icon

        # read the EULA license.txt file
        try:
            with open('data/license.txt', 'r') as license_file:
                license_text = ''.join(license_file.readlines())
        except FileNotFoundError:  # create file if not found
            license_text = 'License file could be found...\n\nPlease contact us at aldras.com/contact for EULA information.'

        vbox_container = wx.BoxSizer(wx.VERTICAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        title_st = wx.StaticText(self, label='Aldras End User License Agreement')
        # change_font(title_st, size=12)
        vbox.Add(title_st, 0, wx.ALIGN_CENTER_HORIZONTAL)

        eula_text = wx.TextCtrl(self, value=license_text, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vbox.Add(eula_text, 1, wx.EXPAND | wx.SOUTH, 10)

        vbox_container.Add(vbox, 1, wx.EXPAND | wx.EAST | wx.WEST, 10)

        close_btn = wx.Button(self, label='Close')
        close_btn.Bind(wx.EVT_BUTTON, lambda event: self.Close(True))
        vbox_container.Add(close_btn, 0, wx.ALIGN_RIGHT | wx.SOUTH | wx.EAST, 5)

        self.SetSizer(vbox_container)
        self.Show()


app = wx.App(0)
frame = EULAFrame(None)
app.MainLoop()