from .etc import *
import os


class _Cryptor:
    def __init__(self, ipath) -> None:
        self.ipath = ipath
        self.shuf_order = None
        self.shuf_order_audio = None
        self.out = None
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
            if self.mediainfo["codec_type"] == "audio":
                self.audio_raw = AudioSegment.from_file(self.ipath)
                print(f"Audio track found: {self.mediainfo['codec_name']} {self.mediainfo['sample_rate']}Hz {self.mediainfo['bit_rate']} bits/s")

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
            print(f"Generating key with password")
        np.random.shuffle(shuf_order)
        if password:
            np.random.seed()

        return shuf_order


class Encryptor(_Cryptor):
    # TODO: Support export flag
    def gen_key(self, path=None, password=None):
        if type(self.shuf_order) is np.ndarray:
            raise SZException("`gen_key` was called twice!")

        self.shuf_order = super()._gen_key(height=self.props["height"], password=password)

        if not path:
            if self.props["is_stream"]:
                self.ipath = self.ipath.replace(":", "").replace("/", "")
            path = f"{self.ipath}.key"
        self.shuf_order.tofile(path)
        self.kpath = path

        return self

    # TODO: Add options for reverse
    def gen_audio_key(self, password=None, chunksize=None, export=False):
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

        self.shuf_order_audio = super()._gen_key(height=audio_length, password=password)

        if export or not password:
            path = f"{self.ipath}.szak"
            self.shuf_order_audio.tofile(path)

        self.new_audio_list = np.empty(audio_length, dtype=object)
        for chunk, pos in zip(audio_list, self.shuf_order_audio):
            self.new_audio_list[pos] = chunk

        return self

    def run(self, preview=False, silent=False) -> None:
        if type(self.shuf_order) is not np.ndarray:
            raise SZException("No key found. Use `gen_key` to generate a key first.")

        if self.audio_raw and not preview:
            if type(self.shuf_order_audio) is not np.ndarray:
                raise SZException("No audio key found. Use `gen_audio_key` to generate a key first.")

            from concurrent.futures import ThreadPoolExecutor

            executor = ThreadPoolExecutor()
            audio_sum_future = executor.submit(sum, tqdm(self.new_audio_list, desc="Audio", disable=silent, position=1, leave=True))

        # print(f"Encrypting with keyfile {os.path.basename(self.kpath)}")

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
            frame_arr = frame_arr[self.shuf_order]

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

        if self.audio_raw and not preview:
            audio_enc = audio_sum_future.result()
            audio_enc.export(f"{self.outpath}.sza", bitrate=self.mediainfo["bit_rate"])

            # TODO: Support more formats
            os.system(f"ffmpeg -hide_banner -loglevel error -i {self.outpath} -i {self.outpath}.sza -c copy -map 0:v:0 -map 1:a:0 -f mp4 {self.outpath}.szv")

            if os.path.isfile(f"{self.outpath}.szv"):
                os.remove(self.outpath)
                os.remove(f"{self.outpath}.sza")
                os.rename(f"{self.outpath}.szv", self.outpath)


class Decryptor(_Cryptor):
    def __init__(self, ipath):
        self.unshuf_order = None
        super().__init__(ipath)

    def set_key(self, path=None, password=None):
        if type(self.unshuf_order) is np.ndarray:
            raise SZException("`set_key` was called twice!")

        if path and password:
            raise SZException("Both keypath and password were specified!")

        self.kpath = path

        if self.kpath:
            self.shuf_order = np.fromfile(self.kpath, dtype="int")
            print(f"Decrypting with keyfile {os.path.basename(self.kpath)}")
        elif password:
            self.shuf_order = super()._gen_key(height=self.props["height"], password=password)
        else:
            raise SZException("No keypath or password specifed.")

        self.unshuf_order = np.zeros_like(self.shuf_order)
        self.unshuf_order[self.shuf_order] = np.arange(int(self.props["height"]))

        return self

    def run(self, preview=False, silent=False) -> None:
        if type(self.unshuf_order) is not np.ndarray:
            # try_kpath = f"{self.ipath}.key"
            # print(f"`set_key` was not used. Trying default path {try_kpath}.")
            # self.set_key(try_kpath)
            raise SZException("No key found. Use `set_key` to set a key first.")

        for i in tqdm(range(int(self.props["frames"])), disable=silent):
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
            frame_arr = frame_arr[self.unshuf_order]

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
