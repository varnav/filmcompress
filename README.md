# filmcompress

This tool will bulk encode supported videos to HEVC (h.265) format in given directory, with optional recursion
and optional hardware acceleration. Primary use is almost lossless compression of short videos from your 
phone or camera. Will do it's best to preserve metadata and quality.

WARNING: This tool is still in beta, and it replaces existing files. Use at your own risk.

## Supported input file formats:

* mov
* mp4
* m4a
* mkv
* WebM
* avi
* 3gp

## Supported GPUs

* nVidia
* Intel
* AMD
* Autodetect (decode only)

Supports Windows, Linux, MacOS and probably other OSes.

## About hardware encoding

Hardware encoder is multiple times faster, but software encoding (default) provides better quality and compatibility.

## About AV1

Supports experimental av1 encoding with `--av1`. Any `--gpu` settings will be ignored. Encoding is slow (hundreds of
times slower than GPU HEVC), but will produce ~20% smaller file with same quality. Sound will be transcoded to 96 kbps
Opus. Unless you use libaom v2 under Linux (build script included) encoding is extremely slow.

## About FFmpeg

Command-line [FFmpeg](https://ffmpeg.org/) is used for transcoding - you must have it installed in your system.

## Installation

```sh
pip install filmcompress
```

You can download and use it as single Windows binary, see [Releases](https://github.com/varnav/filmcompress/releases/)

Unfortunately antiviruses [don't like packed Python executables](https://github.com/pyinstaller/pyinstaller/issues?q=is%3Aissue+virus), so expect false positives from them if you go this way. Best way is pip.

## Usage examples

### PiPy package

```sh
filmcompress --recursive /home/username/myvideos
```

### Windows executable

You will need [ffmpeg binaries](https://www.gyan.dev/ffmpeg/builds/) in path. It's best to
extract 3 exe files from [archive](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z) to %USERPROFILE%\AppData\Local\Microsoft\WindowsApps

```cmd
./filmcompress.exe --encoder nvidia "c:\Users\username\Pictures\My Vacation"
```

## See also

* [Handbrake](https://handbrake.fr/)
* [Av1an](https://github.com/master-of-zen/Av1an)