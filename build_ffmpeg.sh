#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ $(grep -c avx2 /proc/cpuinfo) == 0 ]
  then echo "AVX2 support required"
  exit
fi

set -ex

export DEBIAN_FRONTEND=noninteractive

export  RUSTFLAGS="-C target-feature=+avx2,+fma"
export  CFLAGS="-march=native -mavx2 -mfma -ftree-vectorize -pipe"

sudo apt-get -y install libass-dev libfreetype6-dev libgnutls28-dev libsdl2-dev libtool python3-pip nasm cmake
sudo apt-get -y install libvdpau-dev libxcb1-dev libxcb-shm0-dev libxcb-xfixes0-dev libunistring-dev
sudo apt-get -y install pkg-config texinfo yasm zlib1g-dev libx265-dev libnuma-dev libfdk-aac-dev libopus-dev

# ffmpeg
# https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu

rm -rf ~/ffmpeg_sources

# libaom
mkdir -p ~/ffmpeg_sources ~/bin
cd ~/ffmpeg_sources
git -C aom pull 2> /dev/null || git clone --depth 1 https://aomedia.googlesource.com/aom
mkdir -p aom_build
cd aom_build
PATH="$HOME/bin:$PATH" cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_SHARED=0 -DENABLE_NASM=1 -DENABLE_TESTS=0 -DAOM_TARGET_CPU=native ../aom
PATH="$HOME/bin:$PATH" make -j$(nproc)
make install

# libsvt
cd ~/ffmpeg_sources
git -C SVT-AV1 pull 2> /dev/null || git clone https://github.com/AOMediaCodec/SVT-AV1.git
mkdir -p SVT-AV1/build
cd SVT-AV1/build
PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DCMAKE_BUILD_TYPE=Release -DBUILD_DEC=OFF -DBUILD_SHARED_LIBS=OFF ..
PATH="$HOME/bin:$PATH" make -j$(nproc)
make install

cd ~/ffmpeg_sources
wget -O ffmpeg-snapshot.tar.bz2 https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg
PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --pkg-config-flags="--static" --extra-cflags="-I$HOME/ffmpeg_build/include" --extra-ldflags="-L$HOME/ffmpeg_build/lib" --extra-libs="-lpthread -lm" --bindir="$HOME/bin" --enable-gpl --enable-gnutls --enable-libaom --enable-libsvtav1 --enable-libass --enable-libfdk-aac --enable-libfreetype --enable-libopus --enable-libx265 --enable-nonfree
PATH="$HOME/bin:$PATH" make -j$(nproc)
make install
hash -r

PATH="$HOME/bin:$PATH"
export PATH

echo 'PATH="$HOME/bin:$PATH' >> ~/.profile
source ~/.profile

ffmpeg -version
ffmpeg -h encoder=libaom-av1


echo 'You may need to add ~/bin to PATH'