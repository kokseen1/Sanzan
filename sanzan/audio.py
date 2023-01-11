import ffmpeg
import os
import io
import requests
import pydub
from pydub.playback import play
import numpy as np
from math import floor

from .keygen import Keygen
from .exceptions import SanzanException

DEFAULT_AUDIO_FORMAT = "wav"


class Audio:
    def __init__(self, input_raw) -> None:
        """
        Input can be file path or URL
        """

        self.keygen = None
        self.audio = None
        self.array = None
        self.input_raw = input_raw

        mediainfo = pydub.utils.mediainfo(self.input_raw)
        if not mediainfo.get("sample_rate"):
            raise SanzanException(f"Input does not contain an audio source!")

    def _read(self, input_file):
        audio = pydub.AudioSegment.from_file(input_file)
        array = np.array(audio.get_array_of_samples())

        # Convert to 2-d array for multichannel
        if audio.channels > 1:
            array = array.reshape((-1, audio.channels))

        return audio, array

    def _load(self):
        if self.audio is not None and self.array is not None:
            return

        if self.input_raw.startswith("http"):
            # Retrieve url as bytes
            print(f"\n[audio] Fetching stream `{self.input_raw}`")
            self.input_raw = io.BytesIO(requests.get(self.input_raw).content)

        print(f"\n[audio] Loading `{self.input_raw}`")
        self.audio, self.array = self._read(self.input_raw)
        print(f"\n[audio] Loaded {len(self.array)} samples @ {self.audio.frame_rate}hz")

    def _write(self, output, sr, sw, array, out_format, denoise, preview):
        # Derive channels from array shape
        channels = array.ndim if (array.ndim > 1 and array.shape[1] > 1) else 1

        if sw == 1:
            y = np.int8(array)
        elif sw == 2:
            y = np.int16(array)
        elif sw == 4:
            y = np.int32(array)

        audio_out = pydub.AudioSegment(y.tobytes(), frame_rate=sr, sample_width=sw, channels=channels)

        if not output:
            if preview:
                play(audio_out)
            return

        raw_output = f"tmp_{output}" if output and denoise else output
        audio_out.export(raw_output, format=out_format)

        if denoise:
            ffmpeg.input(raw_output).filter("afftdn", nr="max", nf="max", nt="w").output(output).run(quiet=True, overwrite_output=True)
            os.remove(raw_output)
        
        if preview:
            play(pydub.AudioSegment.from_file(output))

    def set_password(self, password):
        self.keygen = Keygen(password)

    def encrypt(self, output, padding=True, out_format=DEFAULT_AUDIO_FORMAT, denoise=False, preview=False, light=False):
        """
        Padding will extend the array to the nearest sample rate multiple before shuffling
        so that the length can be derived when decrypting, but introduces trailing junk data.
        Padding must be applied to be resistant to length changes from encoding and compression.
        Lossless decryption can be performed if `padding` is False and `out_format` is lossless.
        """

        if self.keygen is None:
            # TODO: Export key as file
            self.keygen = Keygen()

        self._load()

        target_array = self.array
        target_shape = self.array.shape

        if padding:
            padded_dur = floor(self.audio.duration_seconds) + 1
            # Round up to nearest sample rate multiple to get length of padded array
            padded_length = padded_dur * self.audio.frame_rate
            print(f"\n[audio] Padding to {padded_length} samples ({padded_dur}s)")
            target_shape = (padded_length, self.audio.channels) if self.audio.channels > 1 else padded_length
            target_array = np.resize(self.array, target_shape)

        if light:
            dim_3 = (self.audio.channels,) if self.audio.channels > 1 else ()
            target_array = np.reshape(target_array, (self.audio.frame_rate,-1,) + dim_3)

        shuf_order = self.keygen.generate_key(len(target_array), True)
        shuffled_array = target_array[shuf_order]

        if light:
            shuffled_array = np.reshape(shuffled_array, target_shape)

        self._write(output, self.audio.frame_rate, self.audio.sample_width, shuffled_array, out_format, denoise, preview)

    def decrypt(self, output, padding=True, out_format=DEFAULT_AUDIO_FORMAT, denoise=True, preview=False, light=False):
        """
        The array length used during encryption can be derived by rounding down to the nearest sample rate multiple.
        Lossless decryption can be performed if `padding` is False and `out_format` is lossless during encryption.
        """

        if self.keygen is None:
            raise Exception(f"No key to decrypt with!")

        self._load()

        target_array = self.array
        target_shape = self.array.shape

        if padding:
            # Round down to nearest sample rate multiple
            padded_dur = floor(self.audio.duration_seconds)
            padded_length = padded_dur * self.audio.frame_rate
            print(f"\n[audio] Rounding down to {padded_length} samples ({padded_dur}s)")
            target_shape = (padded_length, self.audio.channels) if self.audio.channels > 1 else padded_length
            target_array = np.resize(self.array, target_shape)

        if light:
            dim_3 = (self.audio.channels,) if self.audio.channels > 1 else ()
            target_array = np.reshape(target_array, (self.audio.frame_rate,-1,) + dim_3)

        unshuf_order = self.keygen.generate_rev_key(len(target_array), True)
        unshuffled_array = target_array[unshuf_order]

        if light:
            unshuffled_array = np.reshape(unshuffled_array, target_shape)

        self._write(output, self.audio.frame_rate, self.audio.sample_width, unshuffled_array, out_format, denoise, preview)
