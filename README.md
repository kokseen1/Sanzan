# Sanzan

[![PyPI Release](https://github.com/kokseen1/Sanzan/actions/workflows/release.yml/badge.svg)](https://github.com/kokseen1/Sanzan/actions/workflows/release.yml)
[![tests](https://github.com/kokseen1/Sanzan/actions/workflows/test.yml/badge.svg)](https://github.com/kokseen1/Sanzan/actions/workflows/test.yml)
[![PyPI Version](https://img.shields.io/pypi/v/sanzan.svg)](https://pypi.python.org/pypi/sanzan/)

Quick and simple video and audio obfuscation

## Demo

Encrypted Video:

![Encrypted](https://raw.githubusercontent.com/kokseen1/Sanzan/main/img/enc.gif?raw=True)

Decrypted Video:

![Decrypted](https://raw.githubusercontent.com/kokseen1/Sanzan/main/img/dec.gif?raw=True)

## Prerequisites

[`ffmpeg`](https://www.ffmpeg.org/download.html) must be installed and in `PATH`.

## Installation

```shell
pip install sanzan
```

## Usage

### Encryption

#### With password

```shell
sz -e original.mp4 -o encrypted.mp4 -pw <password>
```

#### With randomly generated key

```shell
sz -e original.mp4 -o encrypted.mp4
```

#### On streams

```shell
sz -e https://youtu.be/dQw4w9WgXcQ -o encrypted.mp4
```

### Decryption

#### With password

```shell
sz -d encrypted.mp4 -o decrypted.mp4 -pw <password>
```

#### With keyfile

```shell
sz -d encrypted.mp4 -o decrypted.mp4 -k <keyfile>
```

## More Usage

Use the optional `-p` flag to view a real time preview of the output. This flag can be used alone or along with the `-o` argument.

```shell
sz -d encrypted.mp4 -o decrypted.mp4 -k <keyfile> -p
```

Use the optional `-s` flag to hide progress bars. Might improve performance.

Use the optional `-c` flag to specify the audio chunksize. The default is `100`.

Use the optional `-ex` flag to export keyfiles.

When encrypting, use the optional `-k` flag to specify the path of the generated keyfile.

```shell
sz -e original.mp4 -o encrypted.mp4 -k <generated keyfile>
```

## Note

- `cv2.waitKey` is unable to maintain a consistent playback framerate for `cv2.imshow`.

<!-- - `vidgear` is used for streaming, but will fall back to `YDL` if streaming is unavailable. -->

- Audio is ~~not yet~~ finally supported!
