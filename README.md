# filmcompress

This tool will bulk encode supported videos to HEVC (h.265) or AV1 format in given directory, with optional recursion
and optional hardware acceleration. Primary use is recompression of multiple short videos from your phone or 
camera, defaults are tuned for this task. Will do its best to preserve metadata and quality.

## Supported input file formats:

* mov
* mp4
* m4a
* mkv
* webm
* avi
* 3gp

## Supported GPUs

* nVidia
* Intel
* AMD

Hardware support is off by default.

Supports Windows, Linux, macOS and probably other OSes.

## About Roku mode

Made for fast reformatting videos for compatibility with [Roku](https://www.roku.com/) (and probably other smart TVs). 

* Container is mkv
* Subtitles saved as embedded SRT
* Audio is downmixed to stereo, normalized and transcoded to Opus 96k

This will allow soundtrack and subtitle selection, and reduces problems with sound quality.

## About hardware encoding

Hardware encoder is multiple times faster, but software encoding (default) provides better quality and compatibility.
My own testing shows that nVidia 20 series cards and later produce good results, but other cards may lack quality.

See [benchmarks](benchmarks.md).

## About AV1

Supports experimental av1 encoding with `--av1`. Any `--gpu` setting will be ignored. Encoding is slow (hundreds of
times slower than GPU HEVC), but will produce ~20% smaller file with same quality. Sound will be transcoded to 96K Opus with this option.

## About FFmpeg

Command-line [FFmpeg](https://ffmpeg.org/) is used for transcoding - you must have it installed in your system.

## Linux

```sh
pip install filmcompress
filmcompress --recursive /home/username/myvideos -o /home/username/myvideos/compressed
```

### Windows

You can download and use it as single Windows binary, see [Releases](https://github.com/varnav/filmcompress/releases/)

Unfortunately antiviruses [don't like packed Python executables](https://github.com/pyinstaller/pyinstaller/issues?q=is%3Aissue+virus), so expect false positives from them if you go this way. Best way is pip.

You will need [ffmpeg binaries](https://www.gyan.dev/ffmpeg/builds/) in path. It's best to
extract 3 exe files from [archive](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z) to %USERPROFILE%\AppData\Local\Microsoft\WindowsApps
Example with nVidia hardware encoding:

```cmd
./filmcompress.exe --gpu nvidia "c:\\Users\\username\\Pictures\\My Vacation" "c:\\Users\\username\\Pictures\\My Vacation\\compressed"
```

Remember, you need double slashes in Windows.

## Todo

* Output format customization

## See also

* [Encoding UHD 4K HDR10 videos with FFmpeg](https://codecalamity.com/encoding-uhd-4k-hdr10-videos-with-ffmpeg/)
* [Fastflix](https://github.com/cdgriffith/FastFlix) - Cross platform transcoding GUI
* [Videomass](https://pypi.org/project/videomass/) - Cross platform transcoding GUI
* [Unmanic](https://github.com/Josh5/unmanic) - Linux mass trancoder
* [Handbrake](https://handbrake.fr/) - Windows transcoding GUI
* [StaxRip](https://github.com/staxrip/staxrip/) - Windows transcoding GUI
* [Av1an](https://github.com/master-of-zen/Av1an)
* [NVEnv](https://github.com/rigaya/NVEnc)
* [media-autobuild_suite](https://github.com/m-ab-s/media-autobuild_suite)
* List of AV1 tools [here](https://nwgat.ninja/test-driving-aomedias-av1-codec/)