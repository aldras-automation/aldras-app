.SetFont(wx.Font(wx.FontInfo(20)))  # change font size
.SetFont(wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.NORMAL))  # change font size
    family: wx.DECORATIVE, wx.DEFAULT,wx.MODERN, wx.ROMAN, wx.SCRIPT or wx.SWISS
    style: wx.NORMAL, wx.SLANT or wx.ITALIC
    weight: wx.NORMAL, wx.LIGHT, or wx.BOLD

.SetForegroundColour(3 * (150,))  # change font color to (r,g,b)

def change_font(static_text, size=None, family=None, style=None, weight=None, color=None):
    # set default parameters
    size = size if size is not None else 9
    family = family if family is not None else wx.DEFAULT
    style = style if style is not None else wx.NORMAL
    weight = weight if weight is not None else wx.NORMAL

    static_text.SetFont(wx.Font(size, family, style, weight))

    if color is not None:
        static_text.SetForegroundColour(color)