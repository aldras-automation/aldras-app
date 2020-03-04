import os
import wx
import wx.adv
import wx.lib.scrolledpanel


def create_about_frame(self):
    about_info = wx.adv.AboutDialogInfo()
    about_info.SetName('Alderas Automation')
    about_info.SetIcon(wx.Icon('logo.ico'))
    about_info.SetVersion(self.software_version)
    about_info.SetDescription(('Simple, powerful utility for general computer automation.'))
    about_info.SetCopyright('(C) 2020 (Not yet)')
    about_info.SetWebSite('http://www.alderas.com')
    wx.adv.AboutBox(about_info)


def setup_frame(self):
    # setting up the file menu
    file_menu = wx.Menu()
    menu_about = file_menu.Append(wx.ID_ABOUT, 'About', ' Information about Aldras')
    # menu_open = file_menu.Append(wx.ID_OPEN, 'Open', ' Open a file to edit')

    # creating the menu bar
    menu_bar = wx.MenuBar()
    menu_bar.Append(file_menu, 'File')  # Adding the file menu to the menu bar
    self.SetMenuBar(menu_bar)  # adding the menu bar to the Frame)
    self.Bind(wx.EVT_MENU, self.on_about, menu_about)
    # self.Bind(wx.EVT_MENU, self.OnOpen, menu_open

    # assign icon
    self.SetIcon(wx.Icon('logo.ico', wx.BITMAP_TYPE_ICO))

    # set background color
    self.SetBackgroundColour('white')


class WorkflowFrame(wx.Frame):
    def __init__(self, parent, title, workflow_name):
        self.dirname = ''
        wx.Frame.__init__(self, parent, title=title)

        # setup_frame(self)

        # set margin
        self.margin_y = 25
        self.margin_x = 100

        # set software version
        self.software_version = '2020.0.0 Beta'

        # create sizers
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.hbox_outer = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_top = wx.BoxSizer(wx.HORIZONTAL)

        # create north and west margins
        self.vbox_outer.AddSpacer(self.margin_y)
        self.hbox_outer.AddSpacer(self.margin_x)

        # add top panel
        self.top = wx.Panel(self)

        self.top.SetSizer(self.vbox_outer)

        # add workflow title
        self.hbox_top.AddSpacer(10)
        self.title = wx.StaticText(self.top, label='Workflow: {}'.format(workflow_name))
        self.title.SetFont(wx.Font(wx.FontInfo(20)))  # change font size
        self.title_contrast = 60
        self.title.SetForegroundColour(
            (self.title_contrast, self.title_contrast, self.title_contrast))  # change font color to (r,g,b)
        self.hbox_top.Add(self.title, 0, wx.ALIGN_CENTER_VERTICAL)

        self.vbox_outer.Add(self.hbox_top)

        ###############################################################

        # add edit panel
        self.edit = wx.lib.scrolledpanel.ScrolledPanel(self, size=(400, 400))
        self.edit.SetupScrolling()
        self.edit.SetBackgroundColour('#FDDF99')

        # create sizers
        self.vbox_edit = wx.BoxSizer(wx.VERTICAL)
        self.hbox_edit = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_edit2 = wx.BoxSizer(wx.HORIZONTAL)

        self.edit.SetSizer(self.vbox_edit)

        for ii in range(60):
            self.hbox_edit = wx.BoxSizer(wx.HORIZONTAL)

            self.hbox_edit.Add(wx.Button(self.edit, size=wx.Size(50, -1), label='<'))
            self.hbox_edit.Add(wx.Button(self.edit, size=wx.Size(50, -1), label='<'))
            self.hbox_edit.Add(wx.Button(self.edit, size=wx.Size(50, -1), label='<'))
            self.hbox_edit.Add(wx.Button(self.edit, size=wx.Size(50, -1), label='<'))
            self.hbox_edit.Add(wx.Button(self.edit, size=wx.Size(50, -1), label='<'))

            self.vbox_edit.Add(self.hbox_edit)

        self.vbox_outer.Add(self.edit)

        ###############################################################

        # add south margin
        self.vbox_outer.AddSpacer(self.margin_y)
        self.hbox_outer.Add(self.vbox_outer)

        # add east margin
        self.hbox_outer.AddSpacer(self.margin_x)

        self.hbox_outer.SetSizeHints(self)
        self.SetSizer(self.hbox_outer)
        self.Show()


def main():
    app = wx.App(False)
    frame = WorkflowFrame(None, 'Aldras Automation', 'WorkflowA')
    app.MainLoop()


if __name__ == '__main__':
    main()
