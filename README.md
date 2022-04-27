# Bangumi
 
## `enc.py`

Main functionality for encrypting and decrypting videos.

Chunk height `CHUNKSIZE` is determined automatically. Video height must be a multiple of `CHUNKS`.

## `stream.py`

For streaming straight from online source using `pafy`. Streaming high resolution videos is very slow and choppy. Download the whole file and use `enc.py` to decrypt and display in realtime for better performance.

## `funcs.py`

Contains functions used by `numpy.vectorize` for mapping a function across a whole `numpy` array. Currently unused.

## Note

- The proper argument to `cv2.waitKey` is uncertain. Needs more testing.

- Audio is not yet supported.
