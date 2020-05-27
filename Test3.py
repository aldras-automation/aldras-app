import wx
import wx.aui

class MainController:
    def __init__(self):

        self.imagesFrame = ImagesFrameAbs(None)
        self.imagesFrame.SetSize(wx.Size( 1200,800 ))
        self.DisplayImages()

    def DisplayImages(self):

        for i in range(900):
            tile = TilePanelAbs(self.imagesFrame.ImagesScrolledWindow)
            bitmap = wx.Bitmap()
            bitmap.LoadFile('foo.jpg', wx.BITMAP_TYPE_ANY)
            tile.ImageBitmap.SetBitmap(bitmap)
            tile.ImageBitmap.SetScaleMode(wx.StaticBitmap.Scale_AspectFit)

            sizer = self.imagesFrame.ImagesScrolledWindow.GetSizer()
            sizer.Add(tile, 0, wx.EXPAND)

class ImagesFrameAbs ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Images", pos = wx.DefaultPosition, size = wx.Size( 871,606 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.m_mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)

        self.ImagesScrolledWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.ImagesScrolledWindow.SetScrollRate( 20, 20 )
        self.m_mgr.AddPane( self.ImagesScrolledWindow, wx.aui.AuiPaneInfo() .Center() .PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).CentrePane() )

        ImagesGridSizer = wx.GridSizer( 0, 2, 0, 0 )


        self.ImagesScrolledWindow.SetSizer( ImagesGridSizer )
        self.ImagesScrolledWindow.Layout()
        ImagesGridSizer.Fit( self.ImagesScrolledWindow )
        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel2, wx.aui.AuiPaneInfo() .Left() .PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).MinSize( wx.Size( 100,-1 ) ) )

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.m_button2 = wx.Button( self.m_panel2, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer4.Add( self.m_button2, 0, wx.ALL, 5 )


        self.m_panel2.SetSizer( bSizer4 )
        self.m_panel2.Layout()
        bSizer4.Fit( self.m_panel2 )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

    def __del__( self ):
        self.m_mgr.UnInit()


###########################################################################
## Class TilePanelAbs
###########################################################################

class TilePanelAbs ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 291,242 ), style = wx.BORDER_SIMPLE|wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_CAPTIONTEXT ) )
        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.TileImagePanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_DEFAULT|wx.TAB_TRAVERSAL )
        self.TileImagePanel.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        self.ImageBitmap = wx.StaticBitmap( self.TileImagePanel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.ImageBitmap, 0, wx.ALL, 5 )


        self.TileImagePanel.SetSizer( bSizer3 )
        self.TileImagePanel.Layout()
        bSizer3.Fit( self.TileImagePanel )
        bSizer1.Add( self.TileImagePanel, 1, wx.EXPAND |wx.ALL, 5 )

        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        self.TileTextLink = wx.StaticText( self, wx.ID_ANY, u"An image", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.TileTextLink.Wrap( -1 )

        bSizer2.Add( self.TileTextLink, 0, wx.ALL, 5 )

        bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()

    def __del__( self ):
        pass

class MyApp(wx.App):

    def OnInit(self):
        self.frame = MainController().imagesFrame
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        return True

# -------------------------------------------------------------------------------

def main():
    app = MyApp(False)
    app.MainLoop()

# -------------------------------------------------------------------------------

if __name__ == "__main__":
    main()