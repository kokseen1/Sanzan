from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Sanzan",
    version="2.0.2",
    packages=["sanzan"],
    description="Video encryption while maintaining playability.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "numpy",
        "yt-dlp",
        "opencv-python",
        "tqdm",
        "pydub",
        "numba",
        "requests",
        "ffmpeg-python",
        "pyaudio",
    ],
    entry_points={
        "console_scripts": [
            "sz = sanzan.sz:main",
        ]
    },
)
