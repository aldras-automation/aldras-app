import wx


class OtherFrame(wx.Frame):
    """
    Class used for creating frames other than the main one
    """

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.Show()


# class MyPanel(wx.Panel):
#
#     def __init__(self, parent):
#         wx.Panel.__init__(self, parent)
#
#
#         self.frame_number = 1
#
#
#     def on_new_frame(self, event):
#         title = 'SubFrame {}'.format(self.frame_number)
#         frame = OtherFrame(self, title=title)
#         self.frame_number += 1


class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='Main Frame', size=(800, 600))
        panel = wx.Panel(self)
        btn = wx.Button(panel, label='Create New Frame')
        btn.Bind(wx.EVT_BUTTON, self.on_new_frame)
        self.frame_number = 1


        self.Show()

    def on_new_frame(self, event):
        title = 'SubFrame {}'.format(self.frame_number)
        OtherFrame(self, title=title)
        self.frame_number += 1


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()