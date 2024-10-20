#!/bin/bash

# sudo pacstrap -K -c root base vim

# # Commands in here are executed in the chroot
# sudo arch-chroot root /bin/bash <<"EOF"
# mkdir /opt
# cd /opt

# # launch
# git clone https://github.com/helloSystem/launch
# yes | pacman -S qt5-base qt5-tools kwindowsystem git cmake clang --needed
# mkdir launch/build
# cd launch/build
# cmake ..
# EOF


echo "Install an Alpine linux chroot and place it in a folder called 'root'."
read -p "Complete? "

sudo arch-chroot root /bin/sh <<"EOF"
export PATH="$PATH:/bin"
/sbin/apk add git

mkdir -p opt
cd /opt

git clone https://github.com/helloSystem/launch.git
mkdir -p launch/build
cd launch/build
grep ^apk ../README.md | sh
cmake ..
sudo make -j $(nproc) install
cd ../..

git clone https://github.com/helloSystem/Menu.git
mkdir -p Menu/build
cd Menu/build
grep ^apk ../README.md | sh
cmake ..
sudo make -j $(nproc) install
cd ../..

git clone https://github.com/helloSystem/Filer.git
mkdir -p Filer/build
cd Filer/build
grep ^apk ../README.md | sh
cmake ..
sudo make -j $(nproc) install
cd ../..
EOF