import pafy
import cv2
import numpy as np
from enc import getChunks, CHUNKS

CHUNKSIZE = 90

url = "https://youtu.be/"
video = pafy.new(url)
# print(video.getbestvideo().url)
# best = video.getbest(preftype="mp4")
cap = cv2.VideoCapture(video.getbestvideo().url)
CHUNKSIZE = int(cap.get(4)/2/CHUNKS)

success = True
while success:
    success, image = cap.read()
    a = np.array(image, dtype=np.uint8)
    
    chunks = getChunks(a, CHUNKSIZE, True)
    edited = np.append(chunks[-1], chunks[-2], axis=0)
    for chunk in chunks[::-1][2:]:
        edited = np.append(edited, chunk, axis=0)

    cv2.imshow("",edited)
    cv2.waitKey(2)