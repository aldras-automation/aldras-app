pause -------------------- Confirm that the physical EV code signing USB token from Sectigo is plugged in and the SafeNet Authentication client is active.

set exe_file=aldras-setup-2021-1.exe

pause -------------------- Confirm that you would like to attempt code siging of the file "%exe_file%".

signtool sign /a /t http://timestamp.digicert.com /v "C:/Users/Noah Baculi/Documents/aldras-app/installer_windows/Output/%exe_file%"

:: If 'signtool' command is not recognized, ensure that signtool is installed and the folder is added to the PATH.

:: Flags (from https://www.thegeekstuff.com/2017/01/signtool-examples/)
:: 
:: /a – “a” here stands for automatic. This option will select the best signing certificate automatically. Use this option when you may have multiple signing certificate. If you have only one signing certificate, you don’t need to provide this option.
:: /t – “t” here stands time stamp server. Following the /t, you should specify the time stamp server URL. This is important. If you don’t specify this option, when your file is signed, it will not be time stamped. You can use any time stamp server URL. I’ve used the URL from verisign.
:: /v – “v” here stands for verbose. This displays a detailed output of the signtool’s execution. This will also display appropriate success, error, and warning messages.


pause -------------------- Press any key to end the program.