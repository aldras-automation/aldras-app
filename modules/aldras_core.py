"""Aldras module containing core objects used across classes"""
import re
import wx
import os
from screeninfo import get_monitors
import math
from operator import add
import uuid
import hashlib
import traceback


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
    uu_id = str(uuid.getnode())
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


def float_in(input_string, return_all=False):
    """Returns parsed float from string."""
    floats = re.findall(r'[-+]?\d*\.\d+|\d+', input_string)
    output = float(floats[0])
    if not floats:
        output = float(0)
    elif len(floats) > 1:
        if return_all:
            output = [float(indiv_float) for indiv_float in floats]

    return output


def variable_names_in(input_string):
    """Return variable in string between {{~ and ~}} syntax"""
    variables = re.findall(r'(?<={{~)(.*?)(?=~}})', input_string)
    return variables
    # if len(variables) == 1:
    #     return variables[0]
    # else:
    #     if allow_multiple_vars:
    #         return variables
    #     raise ValueError


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


def block_end_index(lines, loop_start_index):
    indent_val = 0  # starting indent value of zero to be increased by the
    loop_end_index = -1  # return index for all lines after loop if no ending bracket is found in the loop below

    # loop through all lines starting from loop until ending bracket is found
    for loop_line_index, loop_line in enumerate(lines[loop_start_index:]):
        line_first_word = loop_line.strip().split(' ')[0].lower()[:6]

        if loop_line.strip() == '}':
            indent_val -= 1
        elif ('if' in line_first_word) and ('{' in loop_line):
            # increase by 1 for new indent block to account for the corresponding ending bracket that should not signal end of block of interest
            indent_val += 1
        elif ('loop' in line_first_word) and ('{' in loop_line):
            # increase by 1 for new indent block to account for the corresponding ending bracket that should not signal end of block of interest
            indent_val += 1

        if indent_val == 0:  # if ending bracket for block of interest is found
            loop_end_index = loop_start_index + loop_line_index
            break  # stop loop

    return loop_end_index


def exception_handler(error_type, value, trace):
    """Handler for all unhandled exceptions."""

    exception = "".join(traceback.format_exception(error_type, value, trace))

    error_dlg = wx.MessageDialog(None, exception, 'An Error Occurred', wx.YES_NO | wx.CANCEL | wx.ICON_ERROR)
    error_dlg.SetYesNoCancelLabels('Report', 'Quit', 'Return')
    errror_dlg_response = error_dlg.ShowModal()

    if errror_dlg_response == wx.ID_YES:
        # TODO add feedback submission link
        import webbrowser
        webbrowser.open('https://www.aldras.com/')
    elif errror_dlg_response == wx.ID_NO:
        raise SystemExit()


class CharValidator(wx.Validator):
    """ Validates data as it is entered into the text controls. """

    def __init__(self, flag, parent):
        wx.Validator.__init__(self)
        self.flag = flag
        self.parent = parent
        self.Bind(wx.EVT_CHAR, self.on_char)

    def Clone(self):
        """Required Validator method"""
        return CharValidator(self.flag, self.parent)

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def Validate(self, win):  # used when transferred to window
        if self.flag == 'file_name':
            valid = True
            text_ctrl = self.Window
            value = text_ctrl.Value.capitalize()
            proposed_file_name = f'{self.parent.parent.workflow_directory}/{value}.txt'

            if not value.strip():  # if empty string or only spaces
                valid = False
                wx.MessageDialog(None, 'Enter a file name or cancel',
                                 'Invalid file name', wx.OK | wx.ICON_WARNING).ShowModal()

            try:
                if os.path.exists(proposed_file_name):
                    valid = False
                    wx.MessageDialog(None, f'Enter a file name for a file that does not already exist',
                                     'Taken file name', wx.OK | wx.ICON_WARNING).ShowModal()
                else:
                    with open(proposed_file_name, 'w') as _:  # try to create file to validate file name
                        pass
                    os.remove(proposed_file_name)
            except OSError:
                valid = False
                wx.MessageDialog(None, f'Enter a valid file name for your operating system',
                                 'Invalid file name', wx.OK | wx.ICON_WARNING).ShowModal()
            return valid
        else:
            return True

    def on_char(self, event):
        # process character
        keycode = int(event.GetKeyCode())
        if keycode < 256 and not keycode in [8, 127]:  # don't ignore backspace(8) or delete(127)
            key = chr(keycode)
            # return and do not process key if conditions are met
            if self.flag == 'no_alpha' and key in string.ascii_letters:
                return
            if self.flag == 'only_digit' and not (key.isdecimal() or key == '.'):
                return
            if self.flag == 'only_integer' and not key.isdecimal():
                return
            if self.flag == 'coordinate' and not (key.isdecimal() or key == '-'):
                return
            if self.flag == 'file_name':
                invalid_file_characters = ['<', '>', ':', '\"', '\\', '/', '|', '?', '*']
                if key in invalid_file_characters:
                    return
            if self.flag == 'variable_name':
                invalid_variable_characters = ['<', '>', ':', '\"', '\\', '/', '|', '?', '*', '.']
                if key in invalid_variable_characters:
                    return

        event.Skip()
        return


def show_notification(parent, title, message):
    notification = wx.adv.NotificationMessage(title, message, parent)
    notification.SetIcon(wx.Icon('data/aldras.ico', wx.BITMAP_TYPE_ICO))
    notification.Show()
