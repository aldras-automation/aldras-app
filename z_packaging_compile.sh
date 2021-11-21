# get input about whether to package with debugging console window (defaults to no debug on empty input)
read -p "Package with debugging console window? (y/[n]): " debug_input

# remove old package and packaging tools
rm -rf build
rm -rf dist
rm -rf Aldras.spec
rm -rf Aldras-patched.spec

if [[ $debug_input == *"y"* ]]; then
	echo "Packaging with debug console window..."

	echo "Packaging without obfuscation..."
	# package without obfuscation
	pyinstaller --clean --add-data './data;data' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico Aldras.py -y


else
	echo "Packaging without debug console window..."

	echo "Packaging without obfuscation..."
	# package without obfuscation
	pyinstaller --clean -w --add-data './data;data' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico Aldras.py -y
	
fi

# delete old data files
rm -rf dist/Aldras/data/recent_workflows.txt
rm -rf dist/Aldras/data/settings.json

# copy default settings file
cp -i default_settings/settings.json dist/Aldras/data/

# cd into distribution directory and run executable for the first time to regenerate stock files
cd dist/Aldras
./Aldras
cd ../..

read -p "Press Enter to exit" # wait for user to press enter before exiting
