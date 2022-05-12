import shutil
from pathlib import Path
import sanzan as sz
import hashlib

TESTS_DIR = "tests"
VIDEO_FILENAME = "video.mp4"
VIDEO_ENC_FILENAME = "enc.mp4"
VIDEO_DEC_FILENAME = "dec.mp4"
VIDEO_PASSWORD = "p@ssw0rd"


def test_enc_dec(tmp_path):
    video_path = shutil.copy(Path(TESTS_DIR) / VIDEO_FILENAME, tmp_path)

    e = sz.Encryptor(video_path)
    e.gen_key(password=VIDEO_PASSWORD)
    e.set_output(VIDEO_ENC_FILENAME)
    e.run()

    with open(VIDEO_ENC_FILENAME, "rb") as f:
        enc_raw = f.read()
    assert hashlib.sha1(enc_raw).hexdigest() == "8c3a456c57e87a4cb5cb181c11e38971ab660c01"

    d = sz.Decryptor(VIDEO_ENC_FILENAME)
    d.set_key(password=VIDEO_PASSWORD)
    d.set_output(VIDEO_DEC_FILENAME)
    d.run()

    with open(VIDEO_DEC_FILENAME, "rb") as f:
        dec_raw = f.read()
    assert hashlib.sha1(dec_raw).hexdigest() == "474af33ab79d002c3ce390fa9ea8fca38697c1a0"
