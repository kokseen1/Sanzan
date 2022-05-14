from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Sanzan",
    version="0.0.14",
    packages=["sanzan"],
    description="Quick and simple video obfuscation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "youtube-dl==2020.12.2",
        "opencv-python",
        "numpy==1.21.6",
        "vidgear[core]",
    ],
    entry_points={
        "console_scripts": [
            "sz = sanzan.sz:main",
        ]
    },
)
