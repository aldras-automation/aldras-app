import wx
import wx.adv
import os


class PlaceholderTextCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        self.default_text = kwargs.pop('placeholder', '')
        wx.TextCtrl.__init__(self, *args, **kwargs)
        self.on_unfocus(None)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_unfocus)

    def on_focus(self, evt):
        self.SetForegroundColour(wx.BLACK)
        if self.GetValue() == self.default_text:
            self.SetValue('')
        evt.Skip()

    def on_unfocus(self, evt):
        if self.GetValue().strip() == '':
            self.SetValue(self.default_text)
            self.SetForegroundColour(wx.LIGHT_GREY)
        if evt:
            evt.Skip()


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        self.dirname = ''
        wx.Frame.__init__(self, parent, title=title)

        setup_frame(self)

        # add encompassing panel
        self.container = wx.Panel(self)

        # set padding
        self.padding_y = 25
        self.padding_x = 100

        # set software version
        self.software_version = '2020.0.0 Beta'

        self.placeholder_text = wx.StaticText(self.container, label='Placeholder text'.format(self.software_version))

        self.Show()

    def on_about(self, event):
        create_about_frame(self)


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
    def __init__(self, parent, title):
        self.dirname = ''
        wx.Frame.__init__(self, parent, title=title)

        setup_frame(self)

        # add encompassing panel
        self.container = wx.Panel(self)

        # set padding
        self.padding_y = 25
        self.padding_x = 100

        # set software version
        self.software_version = '2020.0.0 Beta'

        # create sizers
        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.vbox_outer.AddSpacer(self.padding_y)

        # add rescaled logo image
        png = wx.Image('logo.png', wx.BITMAP_TYPE_PNG).Scale(150, 150, wx.IMAGE_QUALITY_BICUBIC)
        self.logo_img = wx.StaticBitmap(self.container, wx.ID_ANY, wx.Bitmap(png))
        self.vbox.Add(self.logo_img, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program name text
        self.program_name = wx.StaticText(self.container, label='Aldras Automation')
        self.program_name.SetFont(wx.Font(wx.FontInfo(18)))
        self.program_name_contrast = 60
        self.program_name.SetForegroundColour(
            (self.program_name_contrast, self.program_name_contrast, self.program_name_contrast))
        self.vbox.Add(self.program_name, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add program version text
        self.program_version = wx.StaticText(self.container, label='Version {}'.format(self.software_version))
        self.program_version.SetFont(wx.Font(wx.FontInfo(10)).Italic())
        self.program_version_contrast = 150
        self.program_version.SetForegroundColour(
            (self.program_version_contrast, self.program_version_contrast, self.program_version_contrast))
        self.vbox.Add(self.program_version, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.AddSpacer(self.padding_y)

        # add input field for the workflow name
        self.workflow_name_input = PlaceholderTextCtrl(self.container, -1, placeholder='Workflow', size=(200, -1))
        self.vbox.Add(self.workflow_name_input, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox.AddSpacer(self.padding_y)

        self.hbox.AddSpacer(self.padding_x)
        self.hbox.Add(self.vbox)
        self.hbox.AddSpacer(self.padding_x)

        self.vbox_outer.AddStretchSpacer()
        self.vbox_outer.Add(self.hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.vbox_outer.AddStretchSpacer()

        self.button_array = wx.StdDialogButtonSizer()
        self.cancel_btn = wx.Button(self.container, label='Quit')
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_exit)
        self.button_array.Add(self.cancel_btn)
        self.ok_btn = wx.Button(self.container, label='OK')
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_open_frame)
        self.button_array.Add(self.ok_btn)
        self.vbox_outer.Add(self.button_array, 0, wx.ALIGN_RIGHT)

        self.vbox_outer.AddSpacer(5)

        self.container.SetSizer(self.vbox_outer)
        self.vbox_outer.SetSizeHints(self)

        self.ok_btn.SetFocus()
        self.Show()

    def on_about(self, event):
        create_about_frame(self)

    def on_exit(self, event):
        self.Close(True)  # close the frame.

    def on_open_frame(self, event):
        # directory selector
        # dlg = wx.DirDialog(None, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        # if dlg.ShowModal() == wx.ID_OK:
        #     fdir = dlg.GetPath() + "/"
        #     dlg.SetPath(fdir)
        #     print('You selected: %s\n' % dlg.GetPath())
        # dlg.Destroy()
        if self.workflow_name_input.GetValue() == 'd':
            # create a message dialog box
            dlg = wx.MessageDialog(self,
                                   'Invalid file name.\nPlease try again.',
                                   'Invalid File Name', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()  # show modal
            dlg.Destroy()  # destroy dialog when finished
        else:
            dlg = wx.MessageDialog(None, 'Please confirm that "{}" is your desired workflow.'.format(
                self.workflow_name_input.GetValue()), 'Workflow Name Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()

            if result == wx.ID_YES:
                main_frame = MainFrame(None,
                                       'Aldras Automation - Workflow: {}'.format(self.workflow_name_input.GetValue()))
                main_frame.Show()
                self.on_exit(self)
            else:
                pass  # returns user back to workflow window

    def OnOpen(self, e):
        ''' Open a file'''
        dlg = wx.FileDialog(self, 'Choose a file', self.dirname, '', '*.*', wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.workflow_name_input.SetValue(f.read())
            f.close()
        dlg.Destroy()


app = wx.App(False)
frame = WorkflowFrame(None, 'Aldras Automation')
app.MainLoop()
