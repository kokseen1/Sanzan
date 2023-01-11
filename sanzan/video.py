import os
from numba import njit
import time
from tqdm import tqdm
import cv2

from .keygen import Keygen
from .exceptions import SanzanException

DEFAULT_SCRAMBLE = "rows"


@njit
def _shuffle_rows(frame, order_x):
    for i in range(len(frame)):
        frame[i] = frame[i][order_x]

    return frame


def get_cap_properties(cap):
    props = {}
    props["width"] = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    props["height"] = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    props["frames"] = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    props["fps"] = cap.get(cv2.CAP_PROP_FPS)

    return props


class Video:
    def __init__(self, input_raw) -> None:
        self.t = time.time()
        self.keygen = None
        self.writer = None
        self.input_file = input_raw

        self.cap = cv2.VideoCapture(self.input_file)
        if not self.cap.isOpened():
            raise SanzanException("Invalid video input path or file format specified")

        self.props = get_cap_properties(self.cap)

        if self.props["frames"] < 0 or self.props["fps"] > 1000:
            raise SanzanException(f"Input does not contain a video source!")

    def set_password(self, password):
        self.keygen = Keygen(password)

    def _generate_keys(self, reseed):
        shuf_order_x = self.keygen.generate_key(int(self.props["width"]), reseed)
        shuf_order_y = self.keygen.generate_key(int(self.props["height"]), reseed)

        return shuf_order_x, shuf_order_y

    def _generate_rev_keys(self, reseed):
        unshuf_order_x = self.keygen.generate_rev_key(int(self.props["width"]), reseed)
        unshuf_order_y = self.keygen.generate_rev_key(int(self.props["height"]), reseed)

        return unshuf_order_x, unshuf_order_y

    def _set_output(self, output):
        # Init VideoWriter object
        self.writer = cv2.VideoWriter(
            output,
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.props["fps"],
            (int(self.props["width"]), int(self.props["height"])),
            isColor=True,
        )
        if not self.writer.isOpened():
            os.remove(output)
            raise Exception("Invalid output path or file format specified")

    def _crypt(self, scramble, preview, per_frame, silent, generate_keys_fn):
        order_x = None
        order_y = None

        for i in tqdm(range(int(self.props["frames"])), desc="[video]", disable=silent, position=0):
            success, frame = self.cap.read()
            if not success:
                print(f"Failed to read frame {i}!")
                break

            if per_frame or order_x is None:
                # Generate new keys every frame if `per_frame` is True
                # Otherwise, use the same keys every frame
                order_x, order_y = generate_keys_fn(not per_frame)

            # Shuffle along y-axis
            if scramble != "cols":
                frame = frame[order_y]

            # Shuffle along x-axis
            if scramble != "rows":
                frame = _shuffle_rows(frame, order_x)

            if self.writer:
                self.writer.write(frame)

            if preview:
                cv2.imshow(self.input_file, frame)
                cv2.waitKey(1)

        self.cap.release()
        if self.writer:
            self.writer.release()
        cv2.destroyAllWindows()

    def encrypt(self, output=None, scramble=DEFAULT_SCRAMBLE, preview=False, per_frame=False, silent=False):
        if self.keygen is None:
            # TODO: Export keys
            self.keygen = Keygen()
        if output:
            self._set_output(output)

        self._crypt(scramble, preview, per_frame, silent, self._generate_keys)

    def decrypt(self, output=None, scramble=DEFAULT_SCRAMBLE, preview=False, per_frame=False, silent=False):
        if self.keygen is None:
            raise Exception(f"No key to decrypt with!")
        if output:
            self._set_output(output)

        self._crypt(scramble, preview, per_frame, silent, self._generate_rev_keys)
