from .etc import *
import os
from concurrent.futures import ProcessPoolExecutor


class _Cryptor:
    def __init__(self, ipath, noaudio=False) -> None:
        self.ipath = ipath
        self.shuf_order = None
        self.shuf_order_audio = None
        self.out = None
        self.outpath = None
        self.mediainfo = None
        self.audio_raw = None
        self.new_audio_list = None

        # Path is a stream url
        if self.ipath.startswith("http"):
            from vidgear.gears import CamGear

            self.cap = CamGear(source=self.ipath, stream_mode=True, logging=False).start()
            print(f"Opened stream: {self.ipath}")
        # Path is a file
        else:
            if not os.path.isfile(self.ipath):
                raise FileNotFoundError(f"No such input file: '{self.ipath}'")
            # TODO: Support audio-only usage
            self.cap = cv2.VideoCapture(self.ipath)
            if not self.cap.isOpened():
                raise OSError("Invalid input path or file format specified")
            print(f"Opened file: {os.path.basename(self.ipath)}")

            self.mediainfo = mediainfo(self.ipath)
            if self.mediainfo["codec_type"] == "audio" and not noaudio:
                print(f"Retrieving audio...")
                self.audio_raw = AudioSegment.from_file(self.ipath)
                print(f"Audio track: {self.mediainfo['codec_name']} {self.mediainfo['sample_rate']}Hz")

        self.props = get_properties(self.cap)

    def set_output(self, path=None):
        self.outpath = path
        self.out = cv2.VideoWriter(
            path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.props["fps"],
            (int(self.props["width"]), int(self.props["height"])),
            isColor=True,
        )
        if not self.out.isOpened():
            raise OSError("Invalid output path or file format specified")
        print(f"Writing to: {path}")

        return self

    def _gen_key(self, height, password=None):
        shuf_order = np.arange(int(height))
        if password:
            np.random.seed(bytearray(password, encoding="utf8"))
        np.random.shuffle(shuf_order)
        if password:
            np.random.seed()

        return shuf_order

    def run(self, preview=False, silent=False) -> None:
        caller = self.__class__.__name__
        if caller == "Encryptor":
            order = self.shuf_order
        elif caller == "Decryptor":
            order = self.unshuf_order
        else:
            raise SZException("`run` called by invalid class!")

        if type(order) is not np.ndarray:
            raise SZException("No video key found!")

        # TODO: Support audio preview
        if self.audio_raw and self.outpath:
            if type(self.new_audio_list) is not np.ndarray:
                raise SZException("No audio key found!")

            executor = ProcessPoolExecutor(4)
            worker_load = int(len(self.new_audio_list) / (os.cpu_count() * 5)) + 1
            print(f"Multiprocessing audio: {worker_load} chunks/worker")
            audio_sum_future = executor.map(sum, self._gen_chunks(self.new_audio_list, worker_load))

        for i in tqdm(range(int(self.props["frames"])), desc="Video", disable=silent, position=0):
            # TODO: Skip frame if error
            if self.props["is_stream"]:
                frame = self.cap.read()
                if frame is None:
                    print(f"Failed to read frame {i}!")
                    break
            else:
                success, frame = self.cap.read()
                if not success:
                    print(f"Failed to read frame {i}!")
                    break

            frame_arr = np.array(frame, dtype=np.uint8)
            frame_arr = frame_arr[order]

            if self.out:
                self.out.write(frame_arr)
            if preview:
                cv2.imshow(self.ipath, frame_arr)
                cv2.waitKey(1)

        if self.props["is_stream"]:
            self.cap.stop()
        else:
            self.cap.release()
        if self.out:
            self.out.release()

        if self.audio_raw and self.outpath:
            print(f"Merging audio and video...")
            audio_enc = sum(audio_sum_future)
            audio_enc.export(f"{self.outpath}.sza", bitrate="320k")

            # TODO: Support more formats
            os.system(f"ffmpeg -hide_banner -loglevel error -i {self.outpath} -i {self.outpath}.sza -c copy -map 0:v:0 -map 1:a:0 -f mp4 {self.outpath}.szv")

            if os.path.isfile(f"{self.outpath}.szv"):
                os.remove(self.outpath)
                os.remove(f"{self.outpath}.sza")
                os.rename(f"{self.outpath}.szv", self.outpath)

    def _gen_chunks(self, lst, n):
        for i in range(0, len(lst), n):
            yield lst[i : i + n]


class Encryptor(_Cryptor):
    # TODO: Support export flag
    def gen_key(self, path=None, password=None, export=False):
        if type(self.shuf_order) is np.ndarray:
            raise SZException("`gen_key` was called twice!")

        self.shuf_order = super()._gen_key(height=self.props["height"], password=password)

        if not path:
            if self.props["is_stream"]:
                self.ipath = self.ipath.replace(":", "").replace("/", "")
            path = f"{self.ipath}.szvk"

        if export or not password:
            self.shuf_order.tofile(path)

        return self

    # TODO: Add options for reverse
    def gen_audio_key(self, password=None, chunksize=None, export=False):
        if not self.audio_raw:
            print("No audio stream! Skipping audio key generation")
            return

        if type(self.shuf_order_audio) is np.ndarray:
            raise SZException("`gen_audio_key` was called twice!")

        if not chunksize:
            chunksize = AUDIO_CHUNKSIZE
        print(f"Using audio chunksize of {chunksize}ms")
        audio_iter = self.audio_raw[::chunksize]
        audio_list = list(audio_iter)
        audio_last_chunk_size = len(audio_list[-1])

        if audio_last_chunk_size != chunksize:
            padding_length = chunksize - audio_last_chunk_size
            print(f"Padding with {padding_length}ms of silence")
            audio_list[-1] += AudioSegment.silent(padding_length)

        audio_length = len(audio_list)
        print(f"No. of chunks: {audio_length}")

        self.shuf_order_audio = super()._gen_key(height=audio_length, password=password)

        # TODO: Change key output path to outpath
        if export or not password:
            path = f"{self.ipath}.szak"
            self.shuf_order_audio.tofile(path)

        self.new_audio_list = np.empty(audio_length, dtype=object)
        for chunk, pos in zip(audio_list, self.shuf_order_audio):
            self.new_audio_list[pos] = chunk

        return self


class Decryptor(_Cryptor):
    def __init__(self, *args, **kwargs):
        self.unshuf_order = None
        super().__init__(*args, **kwargs)

    def set_key(self, path=None, password=None):
        if type(self.unshuf_order) is np.ndarray:
            raise SZException("`set_key` was called twice!")

        # TODO: Prioritise keypath over password
        if path and password:
            raise SZException("Both keypath and password were specified!")

        if path:
            self.shuf_order = np.fromfile(path, dtype="int")
            print(f"Decrypting with keyfile {os.path.basename(path)}")
        elif password:
            self.shuf_order = super()._gen_key(height=self.props["height"], password=password)
        else:
            raise SZException("No keypath or password specifed.")

        video_key_length = len(self.shuf_order)
        if video_key_length != int(self.props["height"]):
            raise SZException(f"Key mismatch! Using key of length {video_key_length} to decrypt video of length {int(self.props['height'])}.")

        self.unshuf_order = np.zeros_like(self.shuf_order)
        self.unshuf_order[self.shuf_order] = np.arange(int(self.props["height"]))

        return self

    def set_audio_key(self, path=None, password=None, chunksize=None):
        if not self.audio_raw:
            print("No audio stream! Skipping audio key generation")
            return

        if type(self.new_audio_list) is np.ndarray:
            raise SZException("`set_audio_key` was called twice!")

        if path and password:
            raise SZException("Both audio keypath and password were specified!")

        if not chunksize:
            chunksize = AUDIO_CHUNKSIZE

        print(f"Using audio chunksize of {chunksize}ms")
        audio_iter = self.audio_raw[::chunksize]
        audio_list = list(audio_iter)
        audio_last_chunk_size = len(audio_list[-1])

        if audio_last_chunk_size != chunksize:
            print(f"Removing last audio chunk of {audio_last_chunk_size}ms")
            del audio_list[-1]

        audio_length = len(audio_list)
        print(f"No. of chunks: {audio_length}")

        if path:
            print(f"Decrypting audio with keyfile {os.path.basename(path)}")
            self.shuf_order_audio = np.fromfile(path, dtype="int")
        elif password:
            self.shuf_order_audio = super()._gen_key(height=audio_length, password=password)
        else:
            raise SZException("No audio keypath or password specifed. Use the `noaudio` flag to ignore audio.")

        self.new_audio_list = np.empty(audio_length, dtype=object)

        audio_key_length = len(self.shuf_order_audio)
        if audio_key_length != audio_length:
            raise SZException(f"Key mismatch! Using key of length {audio_key_length} to decrypt audio of length {audio_length}.")

        for idx, pos in enumerate(self.shuf_order_audio):
            self.new_audio_list[idx] = audio_list[pos]

        return self
