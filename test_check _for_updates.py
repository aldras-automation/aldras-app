from modules.aldras_core import float_in
import webbrowser
import wx
from bs4 import BeautifulSoup
import requests


def check_for_updates(current_version):
    html_page = requests.get('https://aldras.com/assets/html/download_section').text
    soup = BeautifulSoup(html_page, features='html.parser')

    for link in soup.findAll('a'):  # loop through all links
        link_text = link.get('href')
        if '../../downloads/aldras-setup-' in link_text:  # if link has setup executable structure
            version_and_extension = link_text.replace('../../downloads/aldras-setup-', '')
            latest_version = version_and_extension.replace('.exe', '')
            latest_version = latest_version.replace('-', '.')

            if float_in(current_version) < float_in(latest_version):
                # there is a newer version available

                update_available_dlg = wx.MessageDialog(None, f'Aldras version {latest_version} is now available!\n\nWould you like to download the update?', 'Aldras Update Available', wx.YES_NO | wx.ICON_INFORMATION | wx.CENTRE)

                update_available_dlg.SetYesNoLabels('Download', 'Later')  # rename 'Yes' and 'No' labels to 'Download' and 'Later'

                if update_available_dlg.ShowModal() == wx.ID_YES:
                    # download_link = 'https://aldras.com/downloads/aldras-setup-' + version_and_extension
                    download_link = 'https://aldras.com/download'
                    webbrowser.open_new_tab(download_link)


app = wx.App(False)
check_for_updates('2020.0')
app.MainLoop()