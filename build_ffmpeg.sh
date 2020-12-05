#!/bin/sh

sudo apt-get -y install libass-dev libfreetype6-dev libgnutls28-dev libsdl2-dev libtool
sudo apt-get -y install libvdpau-dev libxcb1-dev libxcb-shm0-dev libxcb-xfixes0-dev libunistring-dev
sudo apt-get -y install pkg-config texinfo yasm zlib1g-dev libx265-dev libnuma-dev libfdk-aac-dev libopus-dev

#vmaf
cd /usr/src
rm -rf /usr/src/vmaf
git clone --depth=1 --single-branch --branch v1.5.3 https://github.com/Netflix/vmaf.git
mkdir /usr/local/share/model
cp vmaf/model/* /usr/local/share/model/
cd vmaf/libvmaf
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m virtualenv .venv
source .venv/bin/activate
pip install meson ninja convert
meson build --buildtype release
ninja -vC build
ninja -vC build install
# Oh no not this shit again
cp /usr/local/lib/x86_64-linux-gnu/* /usr/lib/x86_64-linux-gnu/

# ffmpeg
# https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu

mkdir -p ~/ffmpeg_sources ~/bin
cd ~/ffmpeg_sources
git -C aom pull 2> /dev/null || git clone --depth 1 https://aomedia.googlesource.com/aom
mkdir -p aom_build
cd aom_build
PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_SHARED=off -DENABLE_NASM=on -DCONFIG_TUNE_VMAF=1 ../aom
PATH="$HOME/bin:$PATH" make -j4
make install

cd ~/ffmpeg_sources
wget -O ffmpeg-snapshot.tar.bz2 https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg
PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --pkg-config-flags="--static" --extra-cflags="-I$HOME/ffmpeg_build/include" --extra-ldflags="-L$HOME/ffmpeg_build/lib" --extra-libs="-lpthread -lm" --bindir="$HOME/bin" --enable-gpl --enable-gnutls --enable-libaom --enable-libass --enable-libfdk-aac --enable-libfreetype --enable-libopus --enable-libx265 --enable-nonfree --enable-libvmaf
PATH="$HOME/bin:$PATH" make -j4
make install
hash -r

export PATH="$HOME/bin:$PATH"

source ~/.profile

echo "You may need to add ~/bin to PATH"

ffmpeg -version


