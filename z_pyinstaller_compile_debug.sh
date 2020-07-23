# remove old package and packaging tools
rm -rf build
rm -rf dist
rm -rf Aldras.spec

# package without obfuscation
# pyinstaller --add-data 'LexActivator.dll;.' --add-data './data;data' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico Aldras.py -y

# package with obfuscation (pass pyinstaller flags in parentheses after -e)
pyarmor pack -e "--add-data 'LexActivator.dll;.' --add-data './data;data' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico" Aldras.py

# delete old data files
rm -rf dist/Aldras/data/recent_workflows.txt
rm -rf dist/Aldras/data/settings.json

# cd into distribution directory and run executable for the first time to regenerate stock files
cd dist/Aldras
./Aldras
cd ../..