import shutil
from pathlib import Path
import sanzan as sz
import hashlib
import pytest
from sanzan.etc import SZException

TESTS_DIR = "tests"

VIDEO_FILENAME = "video.mp4"
VIDEO_KEYPATH = "keyfile.key"

VIDEO_ENC_FILENAME = "enc.mp4"
VIDEO_DEC_FILENAME = "dec.mp4"

NONEXISTENT_FILENAME = "nonexistent.mp4"
INVALID_FILENAME = "sanzan.invalid"

VIDEO_PASSWORD = "p@ssw0rd"

# VIDEO_ENC_HASH = "8c3a456c57e87a4cb5cb181c11e38971ab660c01"
VIDEO_ENC_HASH = "DBD4F1E1666820C600519A5A2A3799FE3D440CB8"
VIDEO_DEC_HASH = "CC111EBCB17BB01034F6A47AB5FEE6B4A5171814"


def assert_file_hash(filename, hash):
    with open(filename, "rb") as f:
        raw = f.read()
    assert hashlib.sha1(raw).hexdigest() == hash.lower()


def test_enc_dec_pw(tmp_path):
    video_path = shutil.copy(Path(TESTS_DIR) / VIDEO_FILENAME, tmp_path)

    e = sz.Encryptor(video_path)
    e.gen_key(password=VIDEO_PASSWORD)
    e.gen_audio_key(password=VIDEO_PASSWORD)
    e.set_output(VIDEO_ENC_FILENAME)
    e.run()

    assert_file_hash(VIDEO_ENC_FILENAME, VIDEO_ENC_HASH)

    d = sz.Decryptor(VIDEO_ENC_FILENAME)
    d.set_key(password=VIDEO_PASSWORD)
    d.set_audio_key(password=VIDEO_PASSWORD)
    d.set_output(VIDEO_DEC_FILENAME)
    d.run()

    assert_file_hash(VIDEO_DEC_FILENAME, VIDEO_DEC_HASH)


def test_dec_keyfile(tmp_path):
    video_path = shutil.copy(Path(TESTS_DIR) / VIDEO_FILENAME, tmp_path)

    e = sz.Encryptor(video_path)
    e.gen_key(password=VIDEO_PASSWORD)
    e.gen_audio_key(password=VIDEO_PASSWORD, export=True)
    e.set_output(VIDEO_ENC_FILENAME)
    e.run()

    assert_file_hash(VIDEO_ENC_FILENAME, VIDEO_ENC_HASH)

    d = sz.Decryptor(VIDEO_ENC_FILENAME)
    d.set_key(path=tmp_path / Path(VIDEO_FILENAME + ".key"))
    d.set_audio_key(path=tmp_path / Path(VIDEO_FILENAME + ".szak"))
    d.set_output(VIDEO_DEC_FILENAME)
    d.run()

    assert_file_hash(VIDEO_DEC_FILENAME, VIDEO_DEC_HASH)


# Does not work on Github Actions
# def test_dec_keyfile(tmp_path):
#     video_path = shutil.copy(Path(TESTS_DIR) / VIDEO_ENC_FILENAME, tmp_path)
#     key_path = shutil.copy(Path(TESTS_DIR) / VIDEO_KEYPATH, tmp_path)

#     d = sz.Decryptor(video_path)
#     with open(key_path, "rb") as f:
#         raw = f.read()
#     d.set_key(path=key_path)
#     d.set_output(VIDEO_DEC_FILENAME)
#     d.run()

#     assert_file_hash(VIDEO_DEC_FILENAME, VIDEO_DEC_HASH)


def test_enc_no_key_pw(tmp_path):
    with pytest.raises(SZException):
        video_path = shutil.copy(Path(TESTS_DIR) / VIDEO_FILENAME, tmp_path)
        e = sz.Encryptor(video_path)
        e.run()


def test_no_key_pw():
    with pytest.raises(SZException):
        d = sz.Decryptor(VIDEO_ENC_FILENAME)
        d.set_key()

    with pytest.raises(SZException):
        d = sz.Decryptor(VIDEO_ENC_FILENAME)
        d.run()


def test_both_key_pw():
    with pytest.raises(SZException):
        d = sz.Decryptor(VIDEO_ENC_FILENAME)
        d.set_key(path=Path(TESTS_DIR) / VIDEO_KEYPATH, password=VIDEO_PASSWORD)


def test_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        sz.Encryptor(NONEXISTENT_FILENAME)

    with pytest.raises(FileNotFoundError):
        sz.Decryptor(NONEXISTENT_FILENAME)


def test_invalid_format(tmp_path):
    with pytest.raises(OSError):
        video_path = shutil.copy(Path(TESTS_DIR) / VIDEO_FILENAME, tmp_path)
        e = sz.Encryptor(video_path)
        e.set_output(INVALID_FILENAME)
    path = Path(INVALID_FILENAME)
    path.unlink()