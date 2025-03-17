import numpy as np
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D
import scipy
import pyvista as pv
import skimage as sk

def readTextImage(imagePath, raw="vertical"):
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

def saveImage(array, name):
    plt.imshow(array, cmap = "gray")
    plt.axis('off')
    plt.savefig(name,bbox_inches='tight',pad_inches=0)
    return None

def flatFieldCorrect(flatFieldPath, darkFieldPath, samplePath):
    flatField = averageFrames(readTextImage(flatFieldPath))
    darkField = averageFrames(readTextImage(darkFieldPath))
    sampleImage = averageFrames(readTextImage(samplePath))
    flatDarkDiff = (flatField - darkField)+1 # adding one, otherwise div by 0
    correctedImage = (((sampleImage - darkField)+1)/flatDarkDiff)-1
    return correctedImage

def dist(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def make_circle(tiles, cx, cy, r):
    for x in range(cx - r, cx + r):
        for y in range(cy - r, cy + r):
            if dist(cx, cy, x, y) <= r:
                tiles[x][y] = 1

dictionary = np.load('screwHanning.npz')
data = dictionary["arr_0"]

loadedOriginal = data.reshape(data.shape[0], data.shape[1] // 256, 256)
slices = np.transpose(loadedOriginal) # index is now the first

'''
# code below makes a double cone from slices and renders it
size = 256
midpoint = int(np.floor(size/2))
cubeArray = np.zeros((size,size,size))
revCounter = 0
for array in enumerate(cubeArray):
    radius = midpoint
    if array[0] < midpoint:
        r = array[0] +1
        make_circle(array[1], midpoint, midpoint, r)

    elif array[0] >= midpoint:
        r = array[0] - revCounter
        make_circle(array[1], midpoint, midpoint, r)
        revCounter = revCounter + 2

t0 = time.time()
angles = np.arange(0,360)
for slice in enumerate(slices):
    slices[:,:,slice[0]] = sk.transform.iradon(slice[1], theta=angles, filter_name=None, interpolation="nearest")
t1 = time.time()

np.savez("processed.npz", slices)
print(t1-t0)

dictionary = np.load("processed.npz")
data = dictionary["arr_0"]
slices = data

slices = np.transpose(slices)

newslices = np.zeros((256,256,256))
newslices = slices[:256]

#newslices[100] = sk.segmentation.chan_vese(newslices[100])
'''
slices = slices[100:200]
print(np.shape(slices))

opacity = [0, 0, 0, 0, 0, 0, 0, 0, 8, 1, 1, 1, 1, 1] # for screwRampFilter
opacity = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0] # Hanning opaque
opacity = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]

# Create a PyVista grid
grid = pv.ImageData()
grid.dimensions = slices.shape
grid.point_data["values"] = slices.flatten(order="F")  # Add the data to the grid

pl = pv.Plotter()
inter = pl.add_volume(grid, cmap="Greys", opacity=opacity, shade=False)
inter.prop.interpolation_type = "linear" # interpolation smooths out weird clippings

pl.enable_joystick_actor_style()
pl.show()
