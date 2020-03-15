from threading import *
import wx
import wx
from pynput import keyboard, mouse

EVT_RESULT_ID = wx.NewIdRef()


def output_to_file_bkup(output='', end='\n'):
    output = (output + end)
    # with open('{}_bkup.txt'.format(workflow_name), 'a') as record_file:
    #     record_file.write(''.join(output))
    print(output, end='')
    return


def on_press_recording(key):
    global capslock
    global ctrls
    global recording
    output = str(key).strip('\'').lower()
    coords = ''
    df = pd.read_csv('ctrl_keys_ref.csv', names=['Translation', 'Code'])
    df = df.set_index('Code')
    if recording:
        if output == 'key.caps_lock':  # if capslock pressed, swap capslock state
            capslock = not capslock
        if output == 'key.space':  # if capslock pressed, swap capslock state
            output = ' '
        if output == 'key.ctrl_l':  # if left ctrl is pressed, record current mouse position
            coords = pyauto.position()
        if not output.startswith('key'):  # i.e., if output is alphanumeric
            if capslock:
                output = output.swapcase()
        if (output.startswith('\\') and output != '\\\\') or (output.startswith('<') and output.endswith('>')):
            output = '{}'.format(df['Translation'][output.replace('<', '').replace('>', '')])
        if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
            output_to_file_bkup('\\' + '```pressed')
            output = ''
        if output == '\"\'\"':
            output = '\''
        if (not output.startswith('key.ctrl_r')) and (
                not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
            if 'key' in output:
                output = '``' + output
            output = output + '```pressed'
            if coords:
                output = output + ' at {}'.format((coords[0], coords[1]))
            output_to_file_bkup(output)
    if 'key.ctrl_r' in output:
        ctrls += 1
        if not recording:
            print('{}  '.format(ctrls), end='')
            wx.PostEvent(listener_thread._notify_window, ResultEvent('{}'.format(ctrls)))
    if 'key.ctrl_r' in output and ctrls >= 3:  # toggle recording
        ctrls = 0
        recording = not recording
        print()
        print('RECORDING = {}'.format(recording))
        if not recording:
            print('Complete!')
            compile_recording()
            raise SystemExit()
    return


def on_release_recording(key):
    global capslock
    global ctrls
    global recording
    output = str(key).strip('\'').lower()
    coords = ''
    if recording:
        if output == 'key.caps_lock':  # if capslock pressed, swap capslock state
            capslock = not capslock
        if output == 'key.space':  # if capslock pressed, swap capslock state
            output = ' '
        if output == 'key.ctrl_l':  # if left ctrl is pressed, record current mouse position
            coords = pyauto.position()
        if not output.startswith('key'):  # i.e., if output is alphanumeric
            if capslock:
                output = output.swapcase()
        if (output.startswith('\\') and output != '\\\\') or (output.startswith('<') and output.endswith('>')):
            output = 'ctrl+{}'.format(df['Translation'][output.replace('<', '').replace('>', '')])
        if output == '\\\\':  # weird issues with setting output='//' and getting it to print only one slash
            output_to_file_bkup('\\' + '```released')
            output = ''
        if output == '\"\'\"':
            output = '\''
        if (not output.startswith('key.ctrl_r')) and (
                not output.startswith('key.caps_lock')):  # ignore shift and ctrl_r keys
            if 'key' in output:
                output = '``' + output
            output = output + '```released'
            if coords:
                output = output + ' at {}'.format((coords[0], coords[1]))
            output_to_file_bkup(output)
    return


def on_click_recording(x, y, button, pressed):
    if recording:
        output_to_file_bkup('``{}```{} at {}'.format(str(button).lower(), 'pressed' if pressed else 'released', (x, y)))
    return


def on_scroll_recording(x, y, dx, dy):
    if recording:
        output_to_file_bkup('``scrolled.{}```1 at {}'.format('down' if dy < 0 else 'up', (x, y)))
    return


def on_move_recording(x, y):
    # if recording:
    #     output_to_file_bkup('``moved```{}'.format((x, y)))
    return


#
#
def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, int(EVT_RESULT_ID), func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(int(EVT_RESULT_ID))
        self.data = data


# Thread class that executes processing
class ListenerThread(Thread):
    """Worker Thread Class."""

    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        global listener_thread
        listener_thread = self
        self._notify_window = notify_window
        self._want_abort = 0
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # # This is the code executing in the new thread. Simulation of
        # # a long process (well, 10s here) as a simple loop - you will
        # # need to structure your processing so that you periodically
        # # peek at the abort variable
        # for i in range(10):
        #     time.sleep(1)
        #     if self._want_abort:
        #         # Use a result of None to acknowledge the abort (of
        #         # course you can use whatever you'd like or even
        #         # a separate event type)
        #         wx.PostEvent(self._notify_window, ResultEvent(None))
        #         return
        # # Here's where the result would be returned (this is an
        # # example fixed result of the number 10, but it could be
        # # any Python object)

        global recording
        global ctrls
        recording = False
        ctrls = 0

        with mouse.Listener(on_click=on_click_recording, on_scroll=on_scroll_recording,
                            on_move=on_move_recording) as listener:
            with keyboard.Listener(on_press=on_press_recording, on_release=on_release_recording) as listener:
                listener.join()
        wx.PostEvent(self._notify_window, ResultEvent(10))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1


# GUI Frame class that spins off the worker thread
class MainFrame(wx.Frame):
    """Class MainFrame."""

    def __init__(self, parent, id):
        """Create the MainFrame."""
        wx.Frame.__init__(self, parent, id, 'Thread Test')

        # Dumb sample frame with two buttons
        self.btn1 = wx.Button(self, wx.ID_ANY, 'Start', pos=(0, 0))
        self.btn2 = wx.Button(self, wx.ID_ANY, 'Stop', pos=(0, 50))
        self.status = wx.StaticText(self, -1, '', pos=(0, 100))

        self.Bind(wx.EVT_BUTTON, self.OnStart, self.btn1)
        self.Bind(wx.EVT_BUTTON, self.OnStop, self.btn2)

        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)

        # And indicate we don't have a worker thread yet
        self.worker = None

    def OnStart(self, event):
        """Start Computation."""
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            self.status.SetLabel('Starting computation')
            self.worker = ListenerThread(self)

    def OnStop(self, event):
        """Stop Computation."""
        # Flag the worker thread to stop if running
        if self.worker:
            self.status.SetLabel('Trying to abort computation')
            self.worker.abort()

    def OnResult(self, event):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            self.status.SetLabel('Computation aborted')
        else:
            # Process results here
            self.status.SetLabel('Computation Result: %s' % event.data)
        # In either event, the worker is done
        self.worker = None


class MainApp(wx.App):
    """Class Main App."""

    def OnInit(self):
        """Init Main App."""
        self.frame = MainFrame(None, -1)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True


if __name__ == '__main__':
    app = MainApp(0)
    app.MainLoop()
