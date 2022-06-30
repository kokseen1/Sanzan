# Sanzan

[![PyPI Release](https://github.com/kokseen1/Sanzan/actions/workflows/release.yml/badge.svg)](https://github.com/kokseen1/Sanzan/actions/workflows/release.yml)
[![tests](https://github.com/kokseen1/Sanzan/actions/workflows/test.yml/badge.svg)](https://github.com/kokseen1/Sanzan/actions/workflows/test.yml)
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
sz -e original.mp4 -o encrypted.mp4 -pw <password>
```

#### On a stream

```shell
sz -e https://youtu.be/dQw4w9WgXcQ -o encrypted.mp4 -pw <password>
```

### Decryption

#### With preview

```shell
sz -d encrypted.mp4 -o decrypted.mp4 -pw <password> -p
```

#### With a keyfile

Use the `-kv` and `-ka` flags to specify keyfiles when decrypting.

```shell
sz -d encrypted.mp4 -o decrypted.mp4 -kv key.szvk -ka key.szak
```

### More Usage

Omit the `-pw` flag to encrypt using randomly generated keyfiles.

```shell
sz -e original.mp4 -o encrypted.mp4
```

Use the `-s` flag to hide progress bars. This might improve performance slightly.

Use the `-c` flag to specify the audio chunksize. The default is `100`.

Use the `-ex` flag to export the keyfiles generated using a password.

### Python Usage

Alternatively, Sanzan provides a Python interface to programmatically access its functionality.

#### Encryption

```python
from sanzan import Encryptor

PASS = "p@ssw0rd"

if __name__ == "__main__":
    e = Encryptor("video.mp4")
    e.gen_key(password=PASS)
    e.gen_audio_key(password=PASS)
    e.set_output("enc.mp4")
    e.run()
```

#### Decryption

```python
from sanzan import Decryptor

PASS = "p@ssw0rd"

if __name__ == "__main__":
    d = Decryptor("enc.mp4")
    d.set_key(password=PASS)
    d.set_audio_key(password=PASS)
    d.set_output("dec.mp4")
    d.run(preview=True)
```

## Note

- Audio is not supported for streams.
- Previewing audio is not supported.
- Because `cv2.waitKey` is unable to maintain a consistent playback framerate for `cv2.imshow`, preview mode will display frames as quickly as they are produced.
- Container formats like MKV will not decrypt reliably and must be converted to mp4 before encrypting. See this [issue](https://github.com/kokseen1/Sanzan/issues/11#issue-1268649172).
