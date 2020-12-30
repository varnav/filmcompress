import os

from PIL import Image
import tempfile
from click.testing import CliRunner
import requests

from filmcompress import main as conv

tempdir = tempfile.mkdtemp() + os.sep


# tempdir = '/mnt/c/temp/2/'

def file2temp(dl_uri: str) -> str:
    """
    Get file from URL and save it to file (basically wget)
    :param dl_uri: Download URL
    :return: HTTP request status code
    """
    outfile = tempdir + 'videosample1.mp4'
    print("Saving from", dl_uri, "to", outfile)
    try:
        r = requests.get(dl_uri)
        with open(outfile, 'wb') as f:
            f.write(r.content)
            return outfile
    except Exception as e:
        print("Exception:", e)


n1 = file2temp('https://cdn.videvo.net/videvo_files/video/premium/video0243/large_watermarked/02_fireplace_Denoised_20_static_fireplace_preview.mp4')


def test_1():
    runner = CliRunner()
    result = runner.invoke(conv, tempdir)
    assert result.exit_code == 0


def test_2():
    assert os.path.exists(tempdir + 'videosample1.mp4')
