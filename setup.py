import setuptools
import os
import shutil
import filmcompress

if not os.path.exists('filmcompress'):
    os.mkdir('filmcompress')
shutil.copyfile('filmcompress.py', 'filmcompress/__init__.py')

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    'click>=7.1.2',
    'termcolor>=1.1.0',
    'ffmpeg-python>=0.2.0'
]

setuptools.setup(
    name="filmcompress",
    version=filmcompress.__version__,
    author="Evgeny Varnavskiy",
    author_email="varnavruz@gmail.com",
    description="This tool will bulk encode supported videos to HEVC (h.265) or AV1 format in given directory, with optional recursion and optional hardware acceleration.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/varnav/filmcompress",
    keywords=["hevc", "video", "transcoder", "h265", "roku"],
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: GPU :: NVIDIA CUDA",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video :: Conversion",
        "Topic :: Utilities",
        "Environment :: Console",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires='>=3.8',
    entry_points={
        "console_scripts": [
            "filmcompress = filmcompress:main",
        ]
    }
)
