#!/bin/bash
DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get -y install git wget ca-certificates build-essential cmake libtool nasm doxygen python3-pip autoconf automake

#vmaf
cd /usr/src
rm -rf /usr/src/vmaf
git clone --depth=1 https://github.com/Netflix/vmaf.git
cd vmaf/libvmaf
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m virtualenv .venv
source .venv/bin/activate
pip install meson ninja convert
meson build --buildtype release
ninja -vC build
ninja -vC build install

#libaom

cd /usr/src
rm -rf /usr/src/aom
git clone --depth=1 https://aomedia.googlesource.com/aom
cd aom
mkdir build
cd build
# Always this shit
cp /usr/src/vmaf/libvmaf/include/libvmaf/libvmaf.h /usr/include/
cmake -G "Unix Makefiles" -DCONFIG_TUNE_VMAF=1 ..
make -j4
make install

python3 -m pip install av1an