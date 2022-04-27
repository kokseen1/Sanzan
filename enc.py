from random import randint
from PIL import Image
import cv2
import time
import numpy as np
from funcs import *

CHUNKS = 8
CHUNKSIZE = 45

def getChunk(a, idx):
    print(CHUNKSIZE)
    return a[idx*CHUNKSIZE:idx*CHUNKSIZE+CHUNKSIZE]

def getChunks(a,csz,dec=False):
    arr = []
    if not dec:
        for i in range(CHUNKS):
            arr.append(a[i*csz:i*csz + csz])
        return arr
    else:
        for i in range(0,CHUNKS*2,2):
            arr.append(a[i*csz:i*csz + csz])
        return arr

if __name__ == "__main__":
    dflag = False

    og = "f.mp4"
    enc = "enc.mp4"
    dec = "dec.mp4"

    filename = og;outname = enc;fn = np.vectorize(f, otypes=[np.uint8])
    # filename = enc;outname = dec;fn = np.vectorize(f, otypes=[np.uint8]);dflag=True # UNCOMMENT TO DECRYPT

    cap = cv2.VideoCapture(filename)
    success, image = cap.read()

    width = int(cap.get(3))
    height = int(cap.get(4))
    if dflag:height /=2

    CHUNKSIZE = int(height/CHUNKS)
    if not dflag:height*=2

    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Chunk size: {CHUNKSIZE}")
    print(f"FPS: {fps}")
    print(f"Res: {width} x {height}")
    print(f'Mode: {"decrypt" if dflag else "encrypt"}')

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(outname, fourcc, fps, (width, int(height)), isColor=True)
    c = 0

    while success:
        # Convert frame to numpy array
        a = np.array(image, dtype=np.uint8) 
        chunks = getChunks(a, CHUNKSIZE, dflag)

        if not dflag: # encryption
            # random rgb values, not necessary?
            piece = np.array([randint(0,255),randint(0,255),randint(0,255)],dtype=np.uint8)
            rows = np.ones((CHUNKSIZE,width,3),dtype=np.uint8)
            block = rows*piece
            # block = np.full((CHUNKSIZE, width, 3), 0, dtype=np.uint8) # static black block, no performance improvement
            
            edited = np.append(chunks[-1], block, axis=0)
            for chunk in chunks[::-1][1:]:
                edited = np.append(edited, chunk, axis=0)
                edited = np.append(edited, block, axis=0)

        else: # decryption
            edited = np.append(chunks[-1], chunks[-2], axis=0)
            for chunk in chunks[::-1][2:]:
                edited = np.append(edited, chunk, axis=0)

        out.write(edited)
        # cv2.imshow("preview",edited); cv2.waitKey(1) # UNCOMMENT FOR REALTIME PREVIEW

        success, image = cap.read()

        c+=1
        if int(c % fps) == 0:print(f"Progress: {int(c/fps)}s") # UNCOMMENT TO PRINT PROGRESS

    out.release()
