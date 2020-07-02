rm -r build
rm -r dist
rm -r Aldras.spec

pyinstaller -w --add-data 'LexActivator.dll;.' --add-data './data;data' --icon=data/Aldras.ico --hidden-import='pkg_resources.py2_warn' Aldras.py -y