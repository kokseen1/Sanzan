# Sanzan

[![PyPI Release](https://github.com/kokseen1/Sanzan/actions/workflows/release.yml/badge.svg)](https://github.com/kokseen1/Sanzan/actions/workflows/release.yml)
[![PyPI Version](https://img.shields.io/pypi/v/sanzan.svg)](https://pypi.python.org/pypi/sanzan/)

Sanzan is a simple encryption library to encrypt and decrypt videos while maintaining playability.

It uses NumPy and OpenCV to perform video frame manipulation, while using FFmpeg and Pydub for audio manipulation. Sanzan can be used either from the command line or in a Python program.

### Encrypted Video

![Encrypted](https://raw.githubusercontent.com/kokseen1/Sanzan/main/img/enc.gif?raw=True)

### Decrypted Video:

![Decrypted](https://raw.githubusercontent.com/kokseen1/Sanzan/main/img/dec.gif?raw=True)

## Installation

### Prerequisite

[FFmpeg](https://www.ffmpeg.org/download.html) must be installed and in `PATH`.

```shell
pip install sanzan
```

## Usage

### Encryption

```shell
sz original.mp4 -k <key> -e -o encrypted.mp4 
```

#### On a stream

```shell
sz https://youtu.be/dQw4w9WgXcQ -k <key> -e -o encrypted.mp4 
```

### Decryption

```shell
sz encrypted.mp4 -k <key> -d -o decrypted.mp4 
```

#### With preview

```shell
sz encrypted.mp4 -k <key> -d -o decrypted.mp4 -p
```

- Frames will be displayed as quickly as they are generated.
- Audio will only start playing after the whole stream has been processed.

### More Usage

Omit the `-k` argument to encrypt using randomly generated keyfiles.

Use the `-m` argument to specify mode: `audio`, `video` or `full` (default).

Use the `-q` flag for quiet mode.

#### Audio options

Use the `-a` argument to specify output audio format: `mp3`, `wav` (default), `flac`, etc.

Use the `-l` flag to use light encryption/decryption.

Use the `-dn` flag to apply denoising to the output audio.

Use the `-pp` flag to disable audio padding.

#### Video options

Use the `-s` argument to specify scramble method: `rows` (default), `cols`, `full`.

Use the `-f` flag to generate a different scramble order every frame.

### Python Usage

Alternatively, Sanzan provides a Python interface to programmatically access its functionality.

#### Encryption

```python
from sanzan import Sanzan

if __name__ == "__main__":
    s = Sanzan("original.mp4")
    s.set_password("1234")
    s.encrypt("encrypted.mp4")
```

#### Decryption

```python
from sanzan import Sanzan

if __name__ == "__main__":
    s = Sanzan("encrypted.mp4")
    s.set_password("1234")
    s.decrypt("decrypted.mp4", preview=True, denoise=True)
```
