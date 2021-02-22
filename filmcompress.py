#!/usr/bin/env python3
# Based on https://geoffruddock.com/bulk-filmcompress-x265-with-ffmpeg/
import fnmatch
import os
import pathlib
from subprocess import run
import sys
from typing import Iterable
import click
from termcolor import colored
# pip install ffmpeg-python
import ffmpeg

__version__ = '0.4.4'
SUPPORTED_FORMATS = ['mp4', 'mov', 'm4a', 'mkv', 'webm', 'avi', '3gp']
SKIPPED_CODECS = ['hevc', 'av1']


# Ported from: https://github.com/victordomingos/optimize-images
def search_files(dirpath: str, recursive: bool) -> Iterable[str]:
    if os.path.isfile(dirpath):
        yield os.path.normpath(dirpath)
    elif recursive:
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
@click.argument('indir', type=click.Path())
@click.argument('outdir', type=click.Path(exists=True, writable=True), required=False)
@click.option('--roku', is_flag=True, help="Prepare file for Roku player")
@click.option('-f', '--oformat', help="Output file format, mp4 is default", default='mp4')
@click.option('-r', '--recursive', is_flag=True, help='Recursive')
@click.option('--av1', help='AV1 codec (experimental)', type=click.Choice(['aom', 'svt', 'rav1e'], case_sensitive=False))
@click.option('-g', '--gpu', type=click.Choice(['nvidia', 'intel', 'amd', 'none'], case_sensitive=False), help='Use GPU of type. Can be: nvidia, intel, amd. Defaults to none (recommended).')
@click.option('-i', '--include', default='*')
@click.option('-n', '--notranscode', is_flag=True, help='Skip any transcoding, good with Roku mode')
def main(indir, av1, outdir=None, oformat='mp4', include='*', recursive=False, gpu='none', roku=False, notranscode=False):
    """ Compress h264 video files in a directory using libx265 codec

         indir: the directory to scan for video files
         outdir: output directory
         recursive: whether to search directory or all its contents
         gpu: type of hardware encoder
         av1: use experimetal av1 encoder

    """

    outdir = pathlib.PurePath(outdir)
    total = 0
    command_line = ''

    if recursive:
        print('Processing recursively starting from', indir)
        recursive = True
    else:
        print('Processing non-recursively starting from', indir)
        recursive = False

    if outdir is None:
        print('No output directory given, processing in informational mode.', indir)

    for fp in search_files(str(indir), recursive=recursive):
        fp = pathlib.PurePath(fp)
        if not fnmatch.fnmatch(fp, include):
            continue
        assert os.path.exists(fp)
        try:
            probe = ffmpeg.probe(fp)
        except ffmpeg.Error as e:
            print(e.stderr, file=sys.stderr)
            sys.exit(1)

        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            print('No video stream found', file=sys.stderr)
            sys.exit(1)
        codec = video_stream['codec_name']
        print(str(fp), "has codec", colored(codec, 'green'))
        if outdir is None:
            continue
        if (codec in SKIPPED_CODECS) and not roku:
            continue
        if not fnmatch.fnmatch(fp, include):
            continue
        if roku:
            # http://www.rokoding.com/index.html
            print(colored('Roku mode', 'magenta'))
            new_fp = outdir.joinpath(fp.with_suffix('.mkv').name)
            if os.path.exists(new_fp):
                print(colored(str(new_fp) + ' exists', 'yellow'))
                continue
            # Workaround for unsupported map in ffmpeg wrapper, we need '-map 0 -map -0:d'
            if notranscode:
                command_line = ['ffmpeg', '-nostdin', '-i', str(fp), '-ac', '2', '-c:a', 'copy', '-c:v', 'copy', '-c:s', 'svt', '-ignore_chapters', '1', '-map_metadata', '0', '-movflags', 'use_metadata_tags', '-map', '0', '-map', '-0:d', str(new_fp)]
            else:
                command_line = ['ffmpeg', '-nostdin', '-i', str(fp), '-ac', '2', '-c:a', 'libopus', '-b:a', '96k', '-af', 'loudnorm=I=-16:LRA=11:TP=-1.5', '-c:v', 'copy', '-c:s', 'svt', '-ignore_chapters', '1', '-map_metadata', '0', '-movflags', 'use_metadata_tags', '-map', '0', '-map', '-0:d', str(new_fp)]

            print(command_line)
            if run(command_line).returncode != 0:
                exit(1)
            else:
                continue
        else:
            new_fp = outdir.joinpath(fp.with_suffix('.' + oformat).name)
            if os.path.exists(new_fp):
                print(colored(str(new_fp) + ' exists', 'yellow'))
                continue
            if os.name == 'nt' and gpu == 'nvidia':
                print(colored('Encoding with nVidia hardware acceleration', 'yellow'))
                # https://slhck.info/video/2017/03/01/rate-control.html
                # https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/
                # ffmpeg -h encoder=hevc_nvenc
                ffmpeg.input(fp).output(str(new_fp), vsync=0, acodec='copy', map=0, vcodec='hevc_nvenc', **{'rc-lookahead': 25}, map_metadata=0, movflags='use_metadata_tags', preset='p6', spatial_aq=1, temporal_aq=1).run()
            elif av1:
                # ffmpeg -h encoder=libaom-av1
                print(colored('Encoding with experimental AV1 encoder', 'yellow'))
                print('AV 1 codec:', colored(av1, 'yellow'))
                if av1 == 'aom':
                    ffmpeg.input(fp).output(str(new_fp), pix_fmt='yuv420p', acodec='libopus', ab='96k', vcodec='libaom-av1', map_metadata=0, movflags='use_metadata_tags', crf=28, preset='slow').run()
                elif av1 == 'svt':
                    # ffmpeg -h encoder=libsvtav1
                    ffmpeg.input(fp).output(str(new_fp), pix_fmt='yuv420p', acodec='libopus', ab='96k', vcodec='libsvtav1', qp=35, preset=5, map_metadata=0, movflags='use_metadata_tags').run()
                elif av1 == 'rav1e':
                    print('Rav1e not yet supported')
                    exit(0)
            else:
                print(colored('Encoding with no hardware acceleration', 'yellow'))
                # CRF 22 rationale: https://codecalamity.com/encoding-uhd-4k-hdr10-videos-with-ffmpeg/
                # ffmpeg -h encoder=libx265
                print(ffmpeg.input(fp).output(str(new_fp), acodec='libopus', ab='64k', vcodec='libx265', crf=22, preset='slow', map_metadata=0, movflags='use_metadata_tags').run())
            saved = os.path.getsize(fp) - os.path.getsize(new_fp)
            assert saved > 0
            total += saved
            print(colored(new_fp, 'green'), 'ready, saved', round(saved / 1024), 'KB')
        print('Total saved', round(total / 1024 / 1024), 'MB')


if __name__ == '__main__':
    main()
