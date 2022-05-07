import numpy as np
from random import randint
from etc import *

WRITEOUT = True
PREVIEW = True

NAME = ""

if __name__ == "__main__":
    cap = cv2.VideoCapture(FILENAME_RAW.format(NAME))
    width, height, fps = get_properties(cap)

    if WRITEOUT:
        out = cv2.VideoWriter(
            FILENAME_ENC.format(NAME),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (int(width), int(height)),
            isColor=True,
        )

    shuf_order = np.arange(height)
    np.random.shuffle(shuf_order)
    shuf_order.tofile(FILENAME_SHUF_ORDER.format(NAME))

    curr_frame = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_arr = np.array(frame, dtype=np.uint8)

        frame_arr = frame_arr[shuf_order]

        curr_frame += 1

        if WRITEOUT:
            out.write(frame_arr)
        if PREVIEW:
            cv2.imshow("", frame_arr)
            cv2.waitKey(10)
            # cv2.waitKey(int(1000 / fps) - 1)
