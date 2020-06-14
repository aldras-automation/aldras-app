import wx
import wx.grid


class GridFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create a wxGrid object
        grid = wx.grid.Grid(self)
        grid.CreateGrid(100, 1)

        # grid.SetRowSize(0, 60)
        # grid.SetColSize(0, 120)

        # And set grid cell contents as strings
        grid.SetCellValue(0, 0, 'Element 1')
        grid.SetCellValue(1, 0, 'Element 2')
        grid.SetCellValue(2, 0, '...')

        vbox.Add(grid, 0, wx.ALIGN_CENTER)

        self.SetSizer(vbox)
        self.Show()


if __name__ == '__main__':

    app = wx.App(0)
    frame = GridFrame(None)
    app.MainLoop()