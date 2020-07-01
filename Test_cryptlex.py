from cryptlex.lexactivator import *
import wx

LexActivator.SetProductData(
    "NjQyMzc5RUY4MDVFNjBGNUJFMTFEQUVDRUQxRDYyMDE=.BfddnhSQPuJwmB/4zlFYRGX3bnWhGlLA4O5hzfc0Vd65K0ZFV1kLrISOica5rO9uXeyBIusyPN6Ljg8o3XiQ/5PeU4flRtc8aGHve0jVNZCsVqVuWKUQFVetZgNeO7EnJW5Erg8KCi61RdINw/YmTQjKEN0IM7x6001s216YF7HV6NBu+5PiKrpVnqe9aF4fEqrkvMFs4HFzOn9dU2ClhnUci73aMAoOHKcAx3NPiCULcqxTrsdFt65l5TIP91feru5T1bP7JDenNYIIP6n7eRiHrXMqOwGHx7zCCydOFTL7hNp+fPE5mskdqKc6ZKjwnotC2IRAUT0abfjEKAX2s3To8x4VSydj5JkYxoiDRwwm+SgJcuhed0dbXDhwRe4qoo7SsrGrlEJ/xObGeHp8W068zHFnR8YfstN34jTfjy+kYxp40qOP+NvpE7wPyWFgvJvDXPsKehG4gMTg+tP9W3GfrRNQeVL3uAKK0Xukyc9vuIgXzNN7d8rRzjHuJdxBI2qP8rD0fZuR0OAlDOO1fCJokSvCu+VHsxAwUBMCTstVSHYp+aHruhipxmGUmqGCPCHyvsyfZKN/9Vk1388EdUjukwl/DQgy5u9uwEADSrkFgXATV6o7VEWPi3fv5GBWyo1M7qeTLymBMjdJjnStIMmBn9aYYYpvBdFawdWvYnDQLfYK8hAbSdxrufyLMBlHj7VrEG73bUmUZR3GveRlHLozoxAV4APFOrCrgR5/Y6k=")
LexActivator.SetProductId("dd026609-97b9-4f48-bb09-32d9481d9e38", PermissionFlags.LA_USER)


def activate_license(license_str):
    try:
        # LexActivator.SetLicenseKey("FDDA5B-49763F-4E9DB5-B96CD4-43C7FE-A3735A")
        LexActivator.SetLicenseKey(license_str)
        status = LexActivator.ActivateLicense()
        if LexStatusCodes.LA_OK == status or LexStatusCodes.LA_EXPIRED == status or LexStatusCodes.LA_SUSPENDED == status:
            return f"License activated successfully: {status}"
        else:
            return f"License activation failed: {status}"
    except LexActivatorException as exception:
        return f"Error code: {exception.code} {exception.message}"


def validate_license():
    try:
        status = LexActivator.IsLicenseGenuine()
        if LexStatusCodes.LA_OK == status:
            return "License is genuinely activated!"
        elif LexStatusCodes.LA_EXPIRED == status:
            return "License is genuinely activated but has expired!"
        elif LexStatusCodes.LA_SUSPENDED == status:
            return "License is genuinely activated but has been suspended!"
        elif LexStatusCodes.LA_GRACE_PERIOD_OVER == status:
            return "License is genuinely activated but grace period is over!"
        else:
            return f"License is not activated: {status}"
    except LexActivatorException as exception:
        return f"Error code: {exception.code} {exception.message}"


class LicenseFrame(wx.Frame):
    """Main frame to select workflow."""

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='License stuff')
        self.license_input = wx.TextCtrl(self, wx.ID_ANY, size=(200, -1))

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.license_input, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.vbox_outer = wx.BoxSizer(wx.VERTICAL)
        self.vbox_outer.AddStretchSpacer()
        self.vbox_outer.Add(self.vbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
        self.vbox_outer.AddStretchSpacer()

        # add buttons
        self.button_array = wx.StdDialogButtonSizer()
        self.activate_btn = wx.Button(self, label='Activate')
        self.activate_btn.Bind(wx.EVT_BUTTON, self.on_activate)
        self.button_array.Add(self.activate_btn)
        self.button_array.AddSpacer(5)
        self.verify_btn = wx.Button(self, label='Verify')
        self.verify_btn.Bind(wx.EVT_BUTTON, self.on_verify)
        self.button_array.Add(self.verify_btn)
        self.vbox_outer.Add(self.button_array, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        # self.vbox_outer.SetSizeHints(self)

        self.SetSizer(self.vbox_outer)
        self.Center()
        self.Show()

    def on_activate(self, _):
        wx.MessageDialog(self, activate_license(self.license_input.GetValue()), 'Activation',
                         wx.OK | wx.ICON_WARNING).ShowModal()

    def on_verify(self, _):
        wx.MessageDialog(self, validate_license(), 'Activation', wx.OK | wx.ICON_INFORMATION).ShowModal()


app = wx.App(False)
LicenseFrame(None)
app.MainLoop()
