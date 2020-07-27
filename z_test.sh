# remove old package and packaging tools
rm -rf build
rm -rf dist
rm -rf test.spec
rm -rf test-patched.spec

cryptlex_file="C:\\Users\\Noah Baculi\\AppData\\Local\\Programs\\Python\\Python38-32\\Lib\\site-packages\\cryptlex\\lexactivator\\libs\\win32\\x86\\LexActivator.dll"

pyinstaller --clean -w --add-data './data;data' --add-data "$cryptlex_file"';.' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico Aldras.py -y
pyarmor pack --clean -e "-w --add-data './data;data' --add-data '$cryptlex_file;.' --hidden-import='pkg_resources.py2_warn' --icon=data/Aldras.ico" test.py

# cd into distribution directory and run executable for the first time to regenerate stock files
cd dist/test
./test
cd ../..

read -p "Press Enter to exit " # wait for user to press enter before exiting
