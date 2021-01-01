import os

import tempfile
from click.testing import CliRunner
import requests

from filmcompress import main as conv


def file2dir(dl_uri: str, path: str) -> str:
    """
    Get file from URL and save it to file (basically wget)
    :param dl_uri: Download URL
    :return: HTTP request status code
    """
    print("Saving from", dl_uri, "to", path)
    try:
        r = requests.get(dl_uri)
        with open(path, 'wb') as f:
            f.write(r.content)
            return path
    except Exception as e:
        print("Exception:", e)


def test_1():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with tempfile.TemporaryDirectory() as td:
            tf = td + os.sep + 'ForBiggerEscapes.mp4'
            file2dir('http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4', tf)
            with tempfile.TemporaryDirectory() as td2:
                result = runner.invoke(conv, [td, '--outdir', td2])
    print(result.stdout)
    assert result.exit_code == 0

# def test_2():
#     assert os.path.exists(tempdir + 'videosample1.mp4')
