cryptlex_file="C:\\Users\\Noah Baculi\\AppData\\Local\\Programs\\Python\\Python38-32\\Lib\\site-packages\\cryptlex\\lexactivator\\libs\\win32\\x86\\LexActivator.dll"

if [ -f "$cryptlex_file" ]; then
	# only execute if cryptlex LexActivator.dll can be located
	echo "The Cryptlex LexActivator.dll was located, proceeding with packing..."

	# get input about whether to package with debugging console window (defaults to no debug on empty input)
	read -p "Package with debugging console window? (y/[n]): " debug_input

	# get input about whether to package with obfuscation (defaults to with obfuscation on empty input)
	read -p "Package with obfuscation? ([y]/n): " obfuscate_input

	# remove old package and packaging tools
	rm -rf build
	rm -rf dist
	rm -rf Aldras.spec
	rm -rf Aldras-patched.spec

	if [[ $debug_input == *"y"* ]]; then
		echo "Packaging with debug console window..."

		if [[ $obfuscate_input == *"n"* ]]; then
			echo "Packaging without obfuscation..."
			# package without obfuscation
			pyinstaller --clean --add-data './data;data' --add-data "$cryptlex_file"';.' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico Aldras.py -y
		
		else
			echo "Packaging with obfuscation..."

			# package with obfuscation (pass pyinstaller flags in parentheses after -e)
			# https://pyarmor.readthedocs.io/en/latest/man.html#pack
			pyarmor pack --clean -e "--add-data './data;data' --add-data '$cryptlex_file;.' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico" Aldras.py
		fi

	else
		echo "Packaging without debug console window..."

		if [[ $obfuscate_input == *"n"* ]]; then
			echo "Packaging without obfuscation..."
			# package without obfuscation
			pyinstaller --clean -w --add-data './data;data' --add-data "$cryptlex_file"';.' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico Aldras.py -y
		
		else
			echo "Packaging with obfuscation..."

			# package with obfuscation (pass pyinstaller flags in parentheses after -e)
			# https://pyarmor.readthedocs.io/en/latest/man.html#pack
			pyarmor pack --clean -e "-w --add-data './data;data' --add-data '$cryptlex_file;.' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico" Aldras.py

		fi
	fi

	# delete old data files
	rm -rf dist/Aldras/data/recent_workflows.txt
	rm -rf dist/Aldras/data/settings.json

	# cd into distribution directory and run executable for the first time to regenerate stock files
	cd dist/Aldras
	./Aldras
	cd ../..

else
	echo "The Cryptlex LexActivator.dll could not be located at "$cryptlex_file"."
	echo "Please verify Cryptlex LexActivator installation and correct path in packaging script."
fi

read -p "Press Enter to exit" # wait for user to press enter before exiting
