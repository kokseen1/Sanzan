import os
import ffmpeg
from pathlib import Path
from multiprocessing import Process

from .youtube import get_direct_url
from .audio import Audio, DEFAULT_AUDIO_FORMAT
from .video import Video, DEFAULT_SCRAMBLE
from .exceptions import SanzanException

DEFAULT_MODE = "full"


class Sanzan:
    def __init__(self, input_raw, mode=DEFAULT_MODE) -> None:
        self.video = None
        self.audio = None
        self.youtube = False

        video_e = None
        audio_e = None

        input_video = input_raw
        input_audio = input_raw

        if input_raw.startswith("http") and "youtu" in input_raw:
            # Convert youtube url to direct urls
            self.youtube = True

        if mode != "audio":
            try:
                if self.youtube:
                    input_video = get_direct_url(input_raw)
                self.video = Video(input_video)
            except SanzanException as e:
                video_e = e

        if mode != "video":
            try:
                if self.youtube:
                    input_audio = get_direct_url(input_raw, audio=True)
                self.audio = Audio(input_audio)
            except SanzanException as e:
                audio_e = e

        if self.video is None and self.audio is None:
            if video_e is not None:
                raise video_e
            if audio_e is not None:
                raise audio_e

        if self.video is None:
            print(f"Will not handle video")
        if self.audio is None:
            print(f"Will not handle audio")

    def set_password(self, password):
        if self.video:
            self.video.set_password(password)
        if self.audio:
            self.audio.set_password(password)

    def merge(self, video_path, audio_path, output_path):
        print(f"Merging `{video_path}` and `{audio_path}` to `{output_path}`")
        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(audio_path)

        if Path(output_path).suffix.lower() == "mkv":
            f = ffmpeg.output(input_video, input_audio, output_path, acodec="copy", vcodec="copy")
        else:
            f = ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_path)

        f.run(quiet=True, overwrite_output=True)

    def _crypt(self, crypt_mode, output, scramble, preview, per_frame, quiet, padding, audio_out_format, denoise, light):
        procs = []

        if self.audio:
            audio_crypt_fn = self.audio.encrypt if crypt_mode == 0 else self.audio.decrypt
            output_audio = f"{output}.{audio_out_format}" if output and self.video else output
            # audio_crypt_fn(output_audio, padding, audio_out_format, denoise)
            procs.append(
                Process(
                    target=audio_crypt_fn,
                    args=(
                        output_audio,
                        padding,
                        audio_out_format,
                        denoise,
                        preview,
                        light,
                    ),
                )
            )

        [p.start() for p in procs]

        if self.video:
            video_crypt_fn = self.video.encrypt if crypt_mode == 0 else self.video.decrypt
            output_video = f"tmp_{output}" if output and self.audio else output
            video_crypt_fn(output_video, scramble, preview, per_frame, quiet)

        [p.join() for p in procs]

        if output and self.video and self.audio:
            self.merge(output_video, output_audio, output)
            os.remove(output_video)
            os.remove(output_audio)

    def encrypt(self, output=None, scramble=DEFAULT_SCRAMBLE, preview=False, per_frame=False, quiet=False, padding=True, audio_out_format=DEFAULT_AUDIO_FORMAT, denoise=False, light=False):
        self._crypt(0, output, scramble, preview, per_frame, quiet, padding, audio_out_format, denoise, light)

    def decrypt(self, output=None, scramble=DEFAULT_SCRAMBLE, preview=False, per_frame=False, quiet=False, padding=True, audio_out_format=DEFAULT_AUDIO_FORMAT, denoise=True, light=False):
        self._crypt(1, output, scramble, preview, per_frame, quiet, padding, audio_out_format, denoise, light)
