import numpy as np
from etc import *
import youtube_dl

WRITEOUT = True
PREVIEW = True
USE_YDL = False

URL = ""
NAME = ""

if __name__ == "__main__":
    cap = None
    if "URL" in globals() and URL:
        try:
            if USE_YDL:
                raise RuntimeError
            from vidgear.gears import CamGear

            # options = {"STREAM_RESOLUTION": "720p"}
            cap = CamGear(source=URL, stream_mode=True, logging=True).start()
        except RuntimeError:
            OPTIONS["outtmpl"] = FILENAME_ENC.format(NAME)
            with youtube_dl.YoutubeDL(OPTIONS) as ydl:
                ydl.download([URL])

    if not cap:
        cap = cv2.VideoCapture(FILENAME_ENC.format(NAME))

    is_stream, width, height, fps, frames = get_properties(cap)

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
        frame_arr = frame_arr[unshuf_order]

        if WRITEOUT:
            out.write(frame_arr)
        if PREVIEW:
            cv2.imshow("", frame_arr)
            cv2.waitKey(1)
            # cv2.waitKey(int(1000 / fps) - 1)

        curr_frame += 1
        if int(curr_frame % fps) == 0:
            print(f"Progress: frame {curr_frame}/{frames}")
