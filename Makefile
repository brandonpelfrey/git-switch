
.PHONY: install
install:
	chmod +x git_switch.py
	mkdir -p ~/.local/bin
	cp git_switch.py ~/.local/bin/git-switch