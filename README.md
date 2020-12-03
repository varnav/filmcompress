# filmcompress

This tool will bulk encode supported videos to HEVC (h.265) format in given directory, with optional recursion and optional hardware acceleration. Primary use is almost lossless compression of short videos from your phone or camera.

WARNING: This tool is still in beta, and it replaces existing files. Use at your own risk.

## Supported file formats:

* mov
* mp4
* m4a
* mkv

## Supported GPUs

* nVidia
* Intel
* AMD

Supports Windows, Linux, MacOS and probably other OSes.

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
filmcompress --encoder nvidia --recursive /home/username/myvideos
```

### Windows executable

```cmd
./filmcompress.exe --encoder intel "c:\Users\username\Pictures\My Vacation"
```

## See also

* [Handbrake](https://handbrake.fr/)

