import numpy as np
from random import randint
from vidgear.gears import CamGear
from etc import *
import pafy

WRITEOUT = True
PREVIEW = True

# options = {"STREAM_RESOLUTION": "720p"}
URL = ""

NAME = "kon"

if __name__ == "__main__":
    if URL:
        try:
            cap = CamGear(source=URL, stream_mode=False, logging=True).start() # YouTube Video URL as input
        except RuntimeError:
            video = pafy.new(URL)
            cap = cv2.VideoCapture(video.getbestvideo().url)
    else:
        cap = cv2.VideoCapture(FILENAME_ENC.format(NAME))

    is_stream, width, height, fps = get_properties(cap)

    if WRITEOUT:
        out = cv2.VideoWriter(
            FILENAME_DEC.format(NAME),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (int(width), int(height)),
            isColor=True,
        )

    shuf_order = np.fromfile(FILENAME_SHUF_ORDER.format(NAME), dtype="int")

    curr_frame = 0

    while True:
        if is_stream:
            frame = cap.read()
            if frame is None:
                break
        else:
            success, frame = cap.read()
            if not success:
                break

        frame_arr = np.array(frame, dtype=np.uint8)

        unshuf_order = np.zeros_like(shuf_order)
        unshuf_order[shuf_order] = np.arange(height)
        frame_arr = frame_arr[unshuf_order]  # Unshuffle the shuffled data

        curr_frame += 1

        if WRITEOUT:
            out.write(frame_arr)
        if PREVIEW:
            cv2.imshow("", frame_arr)
            cv2.waitKey(10)
            # cv2.waitKey(int(1000 / fps) - 1)
