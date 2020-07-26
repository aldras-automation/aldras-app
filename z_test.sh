# remove old package and packaging tools
rm -rf build
rm -rf dist
rm -rf test.spec
rm -rf test-patched.spec

pyinstaller -w test.py -y

# cd into distribution directory and run executable for the first time to regenerate stock files
cd dist/test
./test
cd ../..

read -p "Press Enter to exit " # wait for user to press enter before exiting
