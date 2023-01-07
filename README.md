# CursedNMAP
A simple front-end to make nmap usage easy for people that have trouble memorizing the command line arguments(like me), and also want to have the output formatted a bit nicer.
## Dependencies
### python3-nmap
Debian/Ubuntu/Mint: apt install python3-nmap
Arch(AUR): https://aur.archlinux.org/packages/python-nmap
Pypi: pip install python-nmap
### nmap(duuh)
Debian/Ubuntu/Mint: apt install nmap
Arch: pacman -S nmap
Gentoo: seriously? if you are using gentoo you shouldn't be needing help to install nmap
### Install(optional)
git clone https://github.com/costagabbie/cursednmap.git
cd cursednmap
sudo cp cnmap.py /usr/bin/cnmap
sudo chmod +x /usr/bin/cnmap
## Usage
On the main screen press F1 to start a new scan, a dialog will open up, where you will be asked the target ip address(or range), and the scan type, use the up and down arrow keys to navigate after selecting them, navigate to the “Start Scanning” and press enter, and wait, the results will show up after the scan is finished.
On the main screen you can use up and down arrows, to scroll through the hosts, left and right to scroll through the pages, and tab to switch between the host list and port list.