# remove old package and packaging tools
git status

read -p "Git commit all? (y/n): " continue_input

if [[ $obfuscate_input == *"n"* ]]; then
	echo "Not committing..."

else
	echo "Committing all..."
	read -p "Git commit message: " commit_msg_input
	git add .
	git commit -m "$commit_msg_input"

fi

read -p "Press Enter to exit " # wait for user to press enter before exiting
