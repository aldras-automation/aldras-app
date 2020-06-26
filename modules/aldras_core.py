"""Aldras module containing core objects used across classes"""
import re
import wx
from screeninfo import get_monitors
import math
from operator import add
import subprocess
import hashlib


def get_system_parameters():
    # get display ranges
    monitors = get_monitors()

    x_indiv = [monitor.x for monitor in monitors]
    widths = [monitor.width for monitor in monitors]
    y_indiv = [monitor.y for monitor in monitors]
    heights = [monitor.height for monitor in monitors]

    x_sum = list(map(add, x_indiv, widths))
    y_sum = list(map(add, y_indiv, heights))

    # get unique hardware id
    uu_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()  # internal uuid
    display_id = ''.join([str(item) for item in
                          x_indiv + y_indiv + widths + heights])  # display configuration id by joining display attributes

    config_id = display_id + uu_id
    config_id = hashlib.sha256(config_id.encode()).hexdigest()  # hash using SHA-256
    config_id = int(math.log(int(config_id, 16), 1.01))  # consolidate by taking log of integer representation

    return (min(x_indiv), max(x_sum)), (min(y_indiv), max(y_sum)), config_id


def coords_of(line):
    """Returns tuple of parsed coordinates from string."""

    try:
        x_coord = re.findall(r'[+-]?\d+', re.findall(r'(?<=\()(.*?)(?=,)', line)[0])[
            0]  # find first integer between '(' and','
    except IndexError:
        x_coord = 0
    try:
        y_coord = re.findall(r'[+-]?\d+', re.findall(r'(?<=,)(.*?)(?=\))', line)[0])[
            0]  # find first integer between ',' and')'
    except IndexError:
        y_coord = 0

    return int(x_coord), int(y_coord)


def eliminate_duplicates(list_with_duplicates):
    """Eliminates duplicates from list"""
    seen = set()
    return [x for x in list_with_duplicates if not (x in seen or seen.add(x))]


def float_in(input_string):
    """Returns parsed float from string."""
    floats = re.findall(r'[-+]?\d*\.\d+|\d+', input_string)
    if not floats:
        output = float(0)
    elif len(floats) > 1:
        output = [float(indiv_float) for indiv_float in floats]
    else:
        output = float(floats[0])

    return output


def variable_name_in(input_string):
    """Return variable in string between {{~ and ~}} syntax"""
    variables = re.findall(r'(?<={{~)(.*?)(?=~}})', input_string)
    if len(variables) == 1:
        return variables[0]
    else:
        raise ValueError


def assignment_variable_value_in(input_string):
    """Return string after equals sign"""
    return '='.join(input_string.split('=')[1:])


def conditional_operation_in(input_string, operations):
    """Return matching operation between ~}} and ~ syntax"""
    operation_in = re.search(r'(?<=~}})(.*?)(?=~)', input_string).group().lower()
    matching_operations_in = [element for element in operations if element.lower() in operation_in]
    if len(matching_operations_in) == 0:
        return ''
    return matching_operations_in[0]


def conditional_comparison_in(input_string):
    """Return matching operation between ~ and ~ syntax after variable {{~var~}}"""
    return re.search(r'(?<=~)(.*?)(?=~)', input_string.replace('{{~', '').replace('~}}', '')).group()


class PlaceholderTextCtrl(wx.TextCtrl):
    """Placeholder text ctrl."""

    def __init__(self, *args, **kwargs):
        self.default_text = kwargs.pop('placeholder', '')  # remove default text parameter
        wx.TextCtrl.__init__(self, *args, **kwargs)
        self.on_unfocus(None)
        self.Bind(wx.EVT_KEY_DOWN, textctrl_tab_trigger_nav)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_unfocus)

    def on_focus(self, _):
        self.SetForegroundColour(wx.BLACK)
        if self.GetValue() == self.default_text:
            self.SetValue('')

    def on_unfocus(self, _):
        if self.GetValue().strip() == '':
            self.SetValue(self.default_text)
            self.SetForegroundColour(3 * (120,))


def textctrl_tab_trigger_nav(event):
    """Function to process tab keypresses and trigger panel navigation."""
    if event.GetKeyCode() == wx.WXK_TAB:
        event.EventObject.Navigate()
    event.Skip()
