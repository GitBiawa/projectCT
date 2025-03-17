import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.animation as animation
from numpy import random

def readTextImage(imagePath):
    readFile = open(imagePath, "r")
    stringList = readFile.readlines() # returns list
    stringList = np.array(stringList)

    rowNumber = np.shape(stringList)[0]
    frameNumber = int(rowNumber/256)
    unframedArray = np.zeros((rowNumber,256))

    for x in enumerate(stringList):
        stringList[x[0]] = stringList[x[0]][:-2] # remove newline characters
        for i in enumerate(x[1].split()): # split off the spacings
            unframedArray[x[0],i[0]] = np.array(int(i[1])) # convert strings to int, new dimensions

    # split by frames and put into array of arrays
    frameArray = np.zeros((frameNumber,256,256))
    for i in range(0,frameNumber):
        frameArray[i] = unframedArray[i*256:(i+1)*256]

    return frameArray

def averageFrames(frameArray):
    frameNumber = len(frameArray)

    a = 0
    for i in range(0,frameNumber):
        a = a + frameArray[i]
    averagedFrames = a/frameNumber
    return averagedFrames

def plotImage(array):
    plt.imshow(array, cmap = "gray")
    plt.axis('off')
    plt.show()
    return None

def flatFieldCorrect(flatFieldPath, darkFieldPath, frames):
    flatField = averageFrames(readTextImage(flatFieldPath))
    darkField = averageFrames(readTextImage(darkFieldPath))
    flatDarkDiff = (flatField - darkField)+1 # adding one, otherwise div by 0
    if os.path.exists("ffCorrected.npz") == False:
        print("flat field correcting...")
        for frame in enumerate(frames):
            frames[frame[0]] = (((frame[1]-darkField)+1)/flatDarkDiff)-1 
        np.savez("ffCorrected.npz", frames)
    else:
        print("flat field corrected images found")
        dictionary = np.load("ffCorrected.npz")
        frames = dictionary["arr_0"]

    return frames

def loadData(folderName):
    os.chdir(folder)

    if os.path.exists(folder + "Frames.npz") == False:
        print("no raw .npz file found")
        frames = readTextImage("concat")
        np.savez(folder + "Frames.npz", frames)
    else:
        print("raw .npz file found")
        dictionary = np.load(folder + "Frames.npz")
        frames = dictionary["arr_0"]

    print(np.shape(frames)[0],"raw frames found")
    return frames

def frameCombiner(frames, framesPerAngle):
    newFrameNumber = int(np.shape(frames)[0]/framesPerAngle)
    combinedFrames = np.zeros((newFrameNumber, 256, 256))
    for frameNum in range(newFrameNumber):
        for i in range(framesPerAngle):
            combinedFrames[frameNum] = combinedFrames[frameNum] + frames[frameNum*framesPerAngle+i] 
        combinedFrames[frameNum] = combinedFrames[frameNum]/framesPerAngle
    print("frames combined into", newFrameNumber, "frames")
    return combinedFrames

def animate(data):
    print("animating...")
    fig, ax = plt.subplots(1,1)
    frames = [] # store generated images
    for i in range(len(data)):
        img = ax.imshow(data[i], cmap="grey", animated=True)
        plt.axis('off')
        frames.append([img])

    ani = animation.ArtistAnimation(fig, frames, interval=50, blit=True)
    ani.save(folder + "Animation.mp4")
    print("animation done!")

folder = "screw"
frames = loadData(folder)
combinedFrames = frameCombiner(frames, 3)

flatField = "ffCorrect/light.txt"
darkField = "ffCorrect/dark.txt"
ffCorrected = flatFieldCorrect(flatField, darkField, combinedFrames)

# take absolute value, removes negatives (?)
goof = np.sqrt((ffCorrected*100)**2)

# normalize so that max intensity is 1
for frame in enumerate(goof):
    goof[frame[0]] = frame[1] / np.max(goof[frame[0]])

animate(goof)

'''
tempArray = goof

def averageSurround(permArray, tempArray, frameNum, rowNum, colNum):
    numSurrounded = 0
    runningSum = 0
    
    


    newValue = runningSum / numSurrounded # average of surrounding pixels
    tempArray[frameNum, rowNum, colNum] = newValue 

for frame in enumerate(frames):
    for row in enumerate(frame[1]):
        for col in enumerate(row[1]): 
            if col[1] == frames[frame[0]+1,row[0],col[0]]:
                averageSurround(frame[0],row[0],col[0])'''
#animate(goof)
