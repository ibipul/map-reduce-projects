from tifffile import TiffFile
import io
import zipfile

import numpy as np
import scipy.stats as ss
from numpy.linalg import svd

def readFileInBinary(filename):
    with open(filename, 'rb') as f:
        fbin = f.read()
    f.close()

    return fbin

def getOrthoTif(zfBytes):
    #given a zipfile as bytes (i.e. from reading from a binary file),
    # return a np array of rgbx values for each pixel
    bytesio = io.BytesIO(zfBytes)
    zfiles = zipfile.ZipFile(bytesio, "r")
    #find tif:
    for fn in zfiles.namelist():
        if fn[-4:] == '.tif':#found it, turn into array:
            tif = TiffFile(io.BytesIO(zfiles.open(fn).read()))
            return tif.asarray()

def getTiffAsMatrix(file_path):
    fbinary = readFileInBinary(file_path)
    tiffmat = getOrthoTif(fbinary)
    return tiffmat

def splitTiffArray(tiffmat, filename='dummy.zip'):
    # Each image is 500x500
    kv_list = []
    if len(tiffmat) == 2500:
        # 25 images case
        row_col_chunks = [(i,i+500) for i in range(0,2500,500)]
    elif len(tiffmat) == 5000:
        row_col_chunks = [(i, i + 500) for i in range(0, 5000, 500)]
    else:
        raise ValueError("TIFF file has dimensions other than 2500x2500 or 5000x5000")

    cell_counter = 0
    for x in row_col_chunks:
        for y in row_col_chunks:
            kv_list.append((filename+'-'+str(cell_counter),tiffmat[x[0]:x[1],y[0]:y[1]]))
            cell_counter +=1

    return kv_list

def tilePixelIntensityConverter(kv):
    file_name = kv[0]
    tile = kv[1]
    intensity_converted_img = []
    for row in tile:
        row_intensities = []
        for pixel in row:
            intensity = int((sum(pixel[:3])/3) * (pixel[-1]/100))
            row_intensities.append(intensity)
        intensity_converted_img.append(row_intensities)

    return (file_name, np.array(intensity_converted_img))


