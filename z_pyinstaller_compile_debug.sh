rm -r build
rm -r dist
rm -r Aldras.spec

pyinstaller --add-data 'LexActivator.dll;.' --add-data './data;data' --icon=data/Aldras.ico --hidden-import='pkg_resources.py2_warn' Aldras.py -y