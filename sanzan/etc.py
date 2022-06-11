import cv2
from tqdm import tqdm
import numpy as np
from datetime import timedelta
from pydub import AudioSegment
from pydub.utils import mediainfo

OPTIONS = {
    "format": "bestvideo",
    "extractaudio": False,
}

AUDIO_CHUNKSIZE = 100


class SZException(Exception):
    pass


def get_properties(cap):
    props = {"is_stream": False}

    if hasattr(cap, "stream"):
        props["is_stream"] = True
        cap = cap.stream

    props["width"] = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    props["height"] = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    props["frames"] = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    props["fps"] = cap.get(cv2.CAP_PROP_FPS)

    print()
    print(f"Capture properties:")
    print(f"Width: {props['width']}")
    print(f"Height: {props['height']}")
    print(f"FPS: {props['fps']}")
    print(f"Total Frames: {props['frames']}")
    print(f"Length: {timedelta(seconds=props['frames']/props['fps'])}")
    print(f"Is stream: {props['is_stream']}")
    print()

    return props
