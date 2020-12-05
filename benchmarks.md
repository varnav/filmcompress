# System configuration

CPU: Intel Core i7 10750H  
GPU 1: Intel UHD Comet Lake GT2  
GPU 2: Mobile nVidia GeForce RTX 2060 (Turing microarchitecture)  

Transcoding:  
Windows 10 20H2  
ffmpeg 2020-12-01-git-ba6e2a2d05-essentials_build-www.gyan.dev  
HEVC encoder version 3.4+27-g5163c32d7

VMAF:  
Ubuntu 20.04 WSL2  
ffmpeg N-100180-gdbf8a16  
VMAF 1.5.3  

Source: [Tears of Steel](https://mango.blender.org/download/)

## HD video

Source: http://ftp.nluug.nl/pub/graphics/blender/demo/movies/ToS/ToS-4k-1920.mov  

File size: 704 MB  
h264 (High) (avc1 / 0x31637661), yuv420p, 1920x800 [SAR 1:1 DAR 12:5], 7862 kb/s, 24 fps, 24 tbr, 24 tbn, 48 tbc (default)

### VMAF command line:

```
./build.ffmpeg.sh
ffmpeg -i result.mkv -i ToS-4k-1920.mov.mkv -lavfi libvmaf -report -f null -
```

### Software

`ffmpeg -xerror -i .\ToS-4k-1920.mov -map_metadata 0 -movflags use_metadata_tags -vcodec libx265 -crf 20 -preset slow -acodec copy ToS_cpu.mov`

encoded 17620 frames in 1695.38s (10.39 fps), 4568.08 kb/s, Avg QP:23.91

File size: 416 MB  
VMAF score: 98.601471

### nVidia

`ffmpeg -xerror -vsync 0 -i .\ToS-4k-1920.mov -rc-lookahead 25 -map_metadata 0 -movflags use_metadata_tags -preset p6 -spatial-aq 1 -temporal_aq 1 -cq 26 -vcodec hevc_nvenc -acodec copy ToS_nvenc.mov`

fps=220 q=19.0 Lsize=416202kB time=00:12:14.12 bitrate=4644.3kbits/s speed=9.15x

File size: 406 MB  
VMAF score: 97.881867

### Intel

`ffmpeg -xerror -hwaccel auto -i .\ToS-4k-1920.mov -vcodec hevc_qsv -b:v 6M -acodec copy ToS_intel.mov`

frame=17620 fps=82 q=-0.0 Lsize= 440303kB time=00:12:14.09 bitrate=4913.5kbits/s speed=3.43x

File size: 429 MB  
VMAF score: 97.592410

## 4K video

Source: http://ftp.nluug.nl/pub/graphics/blender/demo/movies/ToS/tearsofsteel_4k.mov

h264 (High) (avc1 / 0x31637661), yuv420p, 3840x1714 [SAR 1:1 DAR 1920:857], 73244 kb/s, 24 fps, 24 tbr, 24 tbn, 48 tbc (default)

File size: 6.27 GB

### VMAF command line:

```
./build.ffmpeg.sh
ffmpeg -i output.mov -i tearsofsteel_4k.mov -lavfi libvmaf=model_path=/usr/local/share/model/vmaf_4k_v0.6.1.pkl -report -f null -
```

### Software

`ffmpeg -xerror -i tearsofsteel_4k.mov -map_metadata 0 -movflags use_metadata_tags -vcodec libx265 -crf 20 -preset slow -acodec copy tos_cpu_4k.mp4`

TBA

### nVidia

`ffmpeg -xerror -vsync 0 -i .\tearsofsteel_4k.mov -rc-lookahead 25 -map_metadata 0 -movflags use_metadata_tags -preset p6 -spatial-aq 1 -temporal_aq 1 -cq 26 -vcodec hevc_nvenc -acodec copy ToS_nvenc_4k.mov`

fps=55 q=19.0 Lsize= 1665538kB time=00:12:13.95 bitrate=18589.7kbits/s speed=2.29x  
File size: 1.58 GB  
VMAF score: 97.851470

## Conclusion

I understand - this is a very limited benchmark. But in my case NVENC produced slightly larger file with slightly better quality (basically, quality equal to software encoding), while transcoding was 12x faster.
Most likely pre-Turing cards will produce worse quality results.  
Intel hardware encoder also performed well.

## See also

* [Computing VMAF with FFmpeg on Windows](https://streaminglearningcenter.com/blogs/lesson-of-the-week-computing-vmaf-with-ffmpeg-on-windows.html)