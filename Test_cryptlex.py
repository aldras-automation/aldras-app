from cryptlex.lexactivator import *
import wx

LexActivator.SetProductData(
    "NEIzQkVCN0FEMkM0RDA1RTNGNTU3QjA2ODE2REQxMEI=.iZTNUzPGGQAXXbqnKy/Oahvijek6P3TQu+nIw7Cw4tqwVWKSnNEmmOyvck+ZNqTKoZXPA4roJaQnbm1Pf4Xl0ADwmA3AKbIw49DJVN4Y8jbPHD+NyVIf8Ehap6P72PjpwgTi68AxUlDutjaTkI1rGJvLawbpfvuezc1SgwB4V46jr+GzeHirvLcRY2CLrPUDPp+fs1Z5MIk+aLLdf4K4RibzERK3VhwKahhusxo7hwfJKXJhZkZjHGSkjcdvXRbb1Wtx5jXv/uxKgczEkU4RmtPnsYYuZ/GHEYTju0JfpUcKUlHH9tOgqZjvmVbwj5nv1K/+YxRlgZOf+JQe1R78C1K9UVixvezpgtUdN1R2BkD9sDfIlDl9VcPDf2spbjNfGczkriRzrWoUapTBzmzWwDzm8pZRdzxK95JBC+l3sbmDa+8DrAG7/0FCusTHmZITI0+OuOlom7FmoEQVvtfyE+XV3uXPRVltGM5D9DGWMHTsETV/4i4udnTZ0VipyElqapf5TgTDxtAGek/nYxXkQPLlgl0vr1Q3CdlBrm8Tr+o3SlO/pZZ7ubQ5kG+Edupg5tRDg0P33oCN8yPKMd3WAvRvDkcboDy7E7MpsVc0tQx63iKbgzeYITne/58aQKdZe+2dD/HhOBJFgRX3Mfkg7nCPUo38Stritrch1sZamej+gVdaViXfw2b0YCxNpZsfMRX0yTuduc8H11+vDK8feRrt+tfBkwFYK1lHLrZk7T4=")
LexActivator.SetProductId("c1f701ce-2ad7-4505-a186-cd9e3eb89416", PermissionFlags.LA_USER)

print(LexActivator.IsTrialGenuine(), LexStatusCodes.LA_OK)


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
