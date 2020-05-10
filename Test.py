import wx

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,-1,'Frame aka window',size=(300,200))
        panel=wx.Panel(self)
        #
        # Use wx.BITMAP_TYPE_ANY rather than wx.BITMAP_TYPE_BMP
        #
        #pic=wx.Image("Discord.bmp", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #
        # or use wx.Bitmap()
        # pic = wx.Bitmap('data/up_arrow.jpg', wx.BITMAP_TYPE_ANY)
        pic = wx.Image('data/up_arrow1.png', wx.BITMAP_TYPE_ANY).Scale(20, 20, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        #
        self.button=wx.BitmapButton(panel, -1, pic, pos=(10,10))
        self.button.SetWindowStyleFlag(wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.doMe, self.button)
        self.Show()

    def doMe(self, event):
        self.Destroy()

if __name__ == "__main__":
      app = wx.App()
      frame = MainFrame()
      app.MainLoop()