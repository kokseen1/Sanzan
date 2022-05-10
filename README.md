# Bangumi

Quick and simple video obfuscation

<p align="center">
  <img src="https://raw.githubusercontent.com/kokseen1/Bangumi/main/img/obfuscated.png" alt="Obfuscated Video"/>
 <p align="center">Obfuscated Video<p align="center">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/kokseen1/Bangumi/main/img/deobfuscated.png" alt="Deobfuscated Video"/>
 <p align="center">Deobfuscated Video<p align="center">
</p>
 
## encrypt.py

For encrypting videos.

- The keyfile is stored in the `shuf/` directory.

## decrypt.py

For decrypting videos.

- The source video is streamed if `URL` is defined. Otherwise, the file defined by `NAME` from the `enc/` directory is used.

## etc.py

Contains parameters and functions used by `encrypt.py` and `decrypt.py`.

## Usage Notes

- The `WRITEOUT` flag determines if the generated file is written to disk into the respective `enc/` and `dec/` directories.

- The `PREVIEW` flag determines if the video is shown in real time as it is being generated.

## Additional Notes

- `cv2.waitKey` is not able to maintain a consistent playback framerate for `cv2.imshow`.

- `vidgear` is used for streaming, but will fall back to `YDL` if streaming is unavailable.

- Audio is not yet supported.
