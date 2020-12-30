#!/usr/bin/env python3
# Based on https://geoffruddock.com/bulk-filmcompress-x265-with-ffmpeg/

import os
import pathlib
import sys
import tempfile
from subprocess import run, check_output
from typing import Iterable

import shutil
import click
from termcolor import colored

__version__ = '0.3.0'
SUPPORTED_FORMATS = ['mp4', 'mov', 'm4a', 'mkv', 'webm', 'avi', '3gp']
SKIPPED_FORMATS = ['hevc', 'av1']


# Ported from: https://github.com/victordomingos/optimize-images
def search_files(dirpath: str, recursive: bool) -> Iterable[str]:
    if recursive:
        for root, dirs, files in os.walk(dirpath):
            for f in files:
                if not os.path.isfile(os.path.join(root, f)):
                    continue
                extension = os.path.splitext(f)[1][1:]
                if extension.lower() in SUPPORTED_FORMATS:
                    yield os.path.join(root, f)
    else:
        with os.scandir(dirpath) as directory:
            for f in directory:
                if not os.path.isfile(os.path.normpath(f)):
                    continue
                extension = os.path.splitext(f)[1][1:]
                if extension.lower() in SUPPORTED_FORMATS:
                    yield os.path.normpath(f)


@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('-r', '--recursive', is_flag=True, help='Recursive')
@click.option('--av1', is_flag=True, help='Use experimental AV1 instead of HEVC (existing HEVC files will be skipped)')
@click.option('--av1an', is_flag=True, help='Use Av1an for AV1 encoding (experimental)')
@click.option('-g', '--gpu', help='Use GPU of type. Can be: nvidia, intel, amd. Defaults to none (recommended).')
@click.option('-i', '--info', is_flag=True, help='Only enumerate codecs. Do not transcode.')
def main(directory, recursive=False, gpu='none', av1=False, info=False, av1an=False):
    """ Compress h264 video files in a directory using libx265 codec with crf=28

    Args:
         directory: the directory to scan for video files
         recursive: whether to search directory or all its contents
         gpu: type of hardware encoder
         av1: use experimetal av1 encoder
         info:
         av1an:

    """

    total = 0
    tempdir = tempfile.mkdtemp()

    if recursive:
        print('Processing recursively starting from', directory)
        recursive = True
    else:
        print('Processing non-recursively starting from', directory)
        recursive = False

    if not os.access(directory, os.W_OK) or not os.path.exists(directory):
        print('No such directory or not writable')
        sys.exit(1)

    for filepath in search_files(str(directory), recursive=recursive):
        fp = pathlib.PurePath(filepath)
        check_codec_cmd = ['ffprobe', '-hide_banner', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', fp]
        codec = check_output(check_codec_cmd).strip().decode('UTF-8')
        print(filepath, "has codec", colored(codec, 'green'))
        if info:
            continue
        if codec not in SKIPPED_FORMATS:
            new_fp = tempdir + os.sep + 'temp_ffmpeg.mp4'
            if os.name == 'nt' and gpu == 'nvidia':
                # https://slhck.info/video/2017/03/01/rate-control.html
                # https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/
                # ffmpeg -h encoder=hevc_nvenc
                convert_cmd = f'ffmpeg -nostdin -xerror -vsync 0 -i "{fp}" -rc-lookahead 25 -map_metadata 0 -movflags use_metadata_tags -cq 22 -preset p6 -spatial-aq 1 -temporal_aq 1 -vcodec hevc_nvenc "{new_fp}" '
                print(colored('Encoding with nVidia hardware acceleration', 'yellow'))
            elif os.name == 'nt' and gpu == 'intel':
                # ffmpeg -h encoder=hevc_qsv
                # Has no CRF mode and produces 1000kbps low quality images on default settings
                # I set bitrate to higher value to counter this
                convert_cmd = f'ffmpeg -nostdin -xerror -hwaccel auto -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec hevc_qsv -b:v 5M "{new_fp}"'
                print(colored('Encoding with Intel hardware acceleration', 'yellow'))
            elif os.name != 'nt' and gpu == 'intel':
                # https://wiki.libav.org/Hardware/vaapi
                convert_cmd = f'ffmpeg -nostdin -xerror -vaapi_device /dev/dri/renderD128 -hwaccel vaapi -hwaccel_output_format vaapi -i "{fp}" -an -vf "format=nv12|vaapi,hwupload" -map_metadata 0 -movflags use_metadata_tags -vcodec hevc_vaapi "{new_fp}"'
                print(colored('Encoding with Intel hardware acceleration', 'yellow'))
            elif os.name == 'nt' and gpu == 'amd':
                convert_cmd = f'ffmpeg -nostdin -xerror -hwaccel auto -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec hevc_amf "{new_fp}"'
                print(colored('Encoding with AMD hardware acceleration', 'yellow'))
            # elif av1 and gpu == 'auto':
            #     print(colored('Encoding with experimental AV1 encoder', 'yellow'))
            #     convert_cmd = f'ffmpeg -nostdin -xerror -hwaccel auto -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec libaom-av1 -strict experimental -acodec libopus {audio_opts} "{new_fp}"'
            # elif gpu == 'auto':
            #     print(colored('Encoding with autodetected HW for decode only', 'yellow'))
            #     convert_cmd = f'ffmpeg -nostdin -xerror -hwaccel auto -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec libx265 -preset slow {audio_opts} "{new_fp}"'
            elif av1:
                # ffmpeg -h encoder=libaom-av1
                print(colored('Encoding with experimental AV1 encoder', 'yellow'))
                if av1an:
                    convert_cmd = f'av1an -i {fp} -a "-c:a libopus -b:a 64k" -o {tempdir}{os.sep}tmp && ffmpeg -nostdin -i {tempdir}{os.sep}tmp -codec copy {new_fp}'
                else:
                    audio_opts = '-b:a 64k'
                    video_opts = '-b:v 0 -crf 32'
                    convert_cmd = f'ffmpeg -nostdin -xerror -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec libaom-av1 -acodec libopus {audio_opts} {video_opts} "{new_fp}"'

            else:
                print(colored('Encoding with no hardware acceleration', 'yellow'))
                convert_cmd = f'ffmpeg -nostdin -xerror -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec libx265 -crf 20 -preset slow "{new_fp}"'
            if os.path.exists(fp):
                conversion = run(convert_cmd, shell=True)
                print(conversion.stdout)
                if conversion.returncode == 0:
                    saved = os.path.getsize(fp) - os.path.getsize(new_fp)
                    total += saved
                    shutil.move(new_fp, fp)
                    print(colored(fp, 'green'), 'ready, saved', round(saved / 1024), 'KB')
                else:
                    os.remove(new_fp)
                    print(colored(fp, 'red'), 'left intact')
            else:
                print(fp, ' not found')
        else:
            print('Skipping file', colored(fp, 'yellow'))
    os.removedirs(tempdir)
    print('Total saved', round(total / 1024 / 1024), 'MB')


if __name__ == '__main__':
    main()
