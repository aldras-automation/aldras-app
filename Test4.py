import wx
import wx.grid
from wx.lib import wordwrap


class CutomGridCellAutoWrapStringRenderer(wx.grid.PyGridCellRenderer):
    def __init__(self):
        wx.grid.PyGridCellRenderer.__init__(self)

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        text = grid.GetCellValue(row, col)
        dc.SetFont( attr.GetFont() )
        text = wordwrap.wordwrap(text, grid.GetColSize(col), dc, breakLongWords = False)
        hAlign, vAlign = attr.GetAlignment()
        if isSelected:
            bg = grid.GetSelectionBackground()
            fg = grid.GetSelectionForeground()
        else:
            bg = attr.GetBackgroundColour()
            fg = attr.GetTextColour()
        dc.SetTextBackground(bg)
        dc.SetTextForeground(fg)
        dc.SetBrush(wx.Brush(bg, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect)
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        text = wordwrap.wordwrap(text, grid.GetColSize(col), dc, breakLongWords = False)
        w, h, lineHeight = dc.GetMultiLineTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return CutomGridCellAutoWrapStringRenderer()


class MyGrid(wx.grid.Grid):
    def __init__(self, parent, table_size, style=wx.WANTS_CHARS):
        wx.grid.Grid.__init__(self, parent, style=style)
        self.CreateGrid(*table_size)
        self.editor = wx.grid.GridCellAutoWrapStringEditor()
        # self.editor = CutomGridCellAutoWrapStringRenderer()
        self.SetDefaultEditor(self.editor)
        self.SetDefaultRenderer(wx.grid.GridCellAutoWrapStringRenderer())
        self.SetCellValue(0, 0, "Line1\nLine2\nLine3")
        self.SetRowSize(0, 100)
        # self.SetDefaultRenderer(CutomGridCellAutoWrapStringRenderer())

        # self.Bind(wx.EVT_CHAR_HOOK, self.text_entered)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.autoresize)
        # self.Bind(wx.grid.EVT_GRID_SELECT_CELL, lambda event: self.AutoSizeRows())

    def autoresize(self, event):
        print(event.GetRow())
        self.AutoSizeRow(event.GetRow())

class MyFrame(wx.Frame):

    def __init__(self, parent = None, title = "Multiline"):
        wx.Frame.__init__(self, parent, -1, title)
        # self.Bind(wx.EVT_CHAR_HOOK, self.on_frame_char_hook)
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(vbox)
        grid = MyGrid(panel, table_size=(100,20))
        vbox.Add(grid, 1, wx.EXPAND | wx.ALL, 5)
        self.grid = grid
        btn_exit = wx.Button(panel, -1, "Exit")
        vbox.Add(btn_exit, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

    # #Proceed CTRL+ENTER as newline in the cell editor
    # def on_frame_char_hook(self, event):
    #     if event.CmdDown() and event.GetKeyCode() == wx.WXK_RETURN:
    #         if self.grid.editor.IsCreated():
    #             self.grid.editor.StartingKey(event)
    #         else:
    #             event.Skip
    #     else:
    #         event.Skip()

if __name__ == "__main__":
    app = wx.PySimpleApp()
    f = MyFrame()
    f.Center()
    f.Show()
    app.MainLoop()