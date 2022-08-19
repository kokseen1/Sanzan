from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Sanzan",
    version="1.0.1",
    packages=["sanzan"],
    description="Video encryption while maintaining playability.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "opencv-python==4.5.5.64",
        "numpy==1.22.0",
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
