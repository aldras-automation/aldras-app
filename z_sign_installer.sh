signtool sign /tr http://timestamp.sectigo.com /td sha256 /fd sha256 /a "installer_windwows/Output/aldras-setup-2020-2.exe"

the below functions
signtool sign /a /t http://timestamp.verisign.com/scripts/timstamp.dll /v "C:/Users/Noah Baculi/Documents/aldras-app/installer_windows/Output/aldras-setup-2020-2.exe"