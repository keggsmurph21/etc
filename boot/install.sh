#!/bin/sh

# install script for Debian-based systems

# get OS
OS=unknown
if uname -a | grep debian 1>/dev/null; then
	OS=debian
elif uname -a | grep ubuntu 1>/dev/null; then
	OS=ubuntu
fi

BASE=/media/$(whoami)/live-rw
if [ ! -d $BASE ]; then
	# if we're here, we installed from boot/strap.sh
	$BASE=~/boot
else
	ln -s $BASE/git/etc/boot $BASE/boot
	ln -s $BASE ~/persistent
fi
GDRIVE=/media/$(whoami)/gdrive

# make directories
sudo mkdir $GDRIVE

# make some links
ln -s "$GDRIVE/music/iTunes/iTunes Music/Music/" ~/library

# copy some files

# basic apt tools
if [ $OS=ubuntu ]; then
	sudo add-apt-repository universe
else 
	sudo touch /etc/apt/sources.list
	sudo chmod 0666 /etc/apt/sources.list
	echo "deb http://download.videolan.org/pub/debian/stable/ /
	deb http://download.videolan.org/pub/$OS/stable/ /" >> /etc/apt/sources.list
	sudo chmod 0644 /etc/apt/sources.list
	wget -O - http://download.videolan.org/pub/debian/videolan-apt.asc | sudo apt-key add -
fi
sudo apt update
sudo apt install -y curl git htop gparted python3 nodejs curl telnet hexchat vim libdvdcss2

# alias some stuff
echo "
# CUSTOM STUFF
alias node=nodejs
alias python=python3
alias vplay=$BASE/boot/vplay.sh
alias inet=\"ip address | grep inet\"
alias vu=\"amixer sset Master 5%+\"
alias vd=\"amixer sset Master 5%-\"
alias vm=\"amixer sset Master 0%\"
" >> ~/.bashrc

# more apt
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt install -y npm

# git stuff
git config --global credential.helper cache
git config --global user.email "keggsmurph21@gmail.com"
git config --global user.name "Kevin Murphy"

