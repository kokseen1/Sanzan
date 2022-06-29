from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Sanzan",
    version="0.1.7",
    packages=["sanzan"],
    description="Quick and simple video and audio obfuscation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "youtube-dl==2020.12.2",
        "opencv-python==4.5.5.64",
        "numpy==1.22",
        "vidgear[core]",
        "tqdm==4.46.0",
        "pydub==0.25.1"
    ],
    entry_points={
        "console_scripts": [
            "sz = sanzan.sz:main",
        ]
    },
)
