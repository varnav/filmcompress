#!/usr/bin/env python3
# Based on https://geoffruddock.com/bulk-filmcompress-x265-with-ffmpeg/

import os
import pathlib
import sys
import tempfile
from subprocess import run, check_output
from typing import Iterable

import click
from termcolor import colored

__version__ = '0.1.2'
SUPPORTED_FORMATS = ['mp4', 'mov', 'm4a', 'mkv']


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
@click.option('--recursive', is_flag=True, help='Recursive')
@click.option('--gpu', help='Use GPU of type. Can be: nvidia, intel, amd')
def main(directory, recursive=False, gpu='none'):
    """ Compress h264 video files in a directory using libx265 codec with crf=28

    Args:
         directory: the directory to scan for video files
         recursive: whether to search directory or all its contents
         gpu: type of hardware encoder

    """

    total = 0

    if recursive:
        print('Processing recursively starting from', directory)
        recursive = False
    else:
        print('Processing non-recursively starting from', directory)
        recursive = True

    if not os.access(directory, os.W_OK) or not os.path.exists(directory):
        print('No such directory or not writable')
        sys.exit(1)

    for filepath in search_files(str(directory), recursive=recursive):
        fp = pathlib.PurePath(filepath)
        check_codec_cmd = 'ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of ' \
                          'default=noprint_wrappers=1:nokey=1 "{fp}" '
        codecs = [check_output(check_codec_cmd.format(fp=fp), shell=True).strip().decode('UTF-8')]
        print(filepath, "has codecs", colored(codecs, 'green'))

        if not ('hevc' in codecs):
            tempdir = tempfile.mkdtemp()
            new_fp = tempdir + os.sep + 'temp_ffmpeg.mp4'
            if os.name == 'nt' and gpu == 'nvidia':
                # https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/
                convert_cmd = f'ffmpeg -nostdin -xerror -hwaccel cuda -vsync 0 -i "{fp}" -rc-lookahead 15 -map_metadata 0 -movflags use_metadata_tags -vcodec hevc_nvenc -acodec copy "{new_fp}" '
                print(colored('Using nVidia hardware acceleration', 'yellow'))
            elif os.name != 'nt' and gpu == 'nvidia':
                # https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/
                convert_cmd = f'ffmpeg -nostdin -xerror -vsync 0 -i "{fp}" -rc-lookahead 15 -map_metadata 0 -movflags use_metadata_tags -vcodec hevc_nvenc -acodec copy "{new_fp}" '
                print(colored('Using nVidia hardware acceleration', 'yellow'))
            elif os.name == 'nt' and gpu == 'intel':
                convert_cmd = f'ffmpeg -nostdin -xerror -hwaccel qsv -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec hevc_qsv -acodec copy "{new_fp}"'
                print(colored('Using Intel hardware acceleration', 'yellow'))
            elif os.name != 'nt' and gpu == 'intel':
                convert_cmd = f'ffmpeg -nostdin -xerror -hwaccel vaapi -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec hevc_vaapi -acodec copy "{new_fp}"'
                print(colored('Using Intel hardware acceleration', 'yellow'))
            elif os.name == 'nt' and gpu == 'amd':
                convert_cmd = f'ffmpeg -nostdin -xerror -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec hevc_amf -acodec copy "{new_fp}"'
                print(colored('Using AMD hardware acceleration', 'yellow'))
            else:
                print(colored('Using no hardware acceleration', 'yellow'))
                convert_cmd = f'ffmpeg -nostdin -xerror -i "{fp}" -map_metadata 0 -movflags use_metadata_tags -vcodec libx265 -acodec copy "{new_fp}"'

            conversion_return_code = run(convert_cmd, shell=(os.name != 'nt')).returncode
            if conversion_return_code == 0:
                saved = os.path.getsize(fp) - os.path.getsize(new_fp)
                total += saved
                os.replace(new_fp, fp)
                print(colored(fp, 'green'), 'ready, saved', round(saved / 1024), 'KB')
            else:
                os.remove(new_fp)
                print(colored(fp, 'red'), 'left intact')
            os.removedirs(tempdir)
        else:
            print('Skipping HEVC file', colored(fp, 'yellow'))
    print('Total saved', round(total / 1024 / 1024), 'MB')


if __name__ == '__main__':
    main()
