from numpy import genfromtxt
import numpy as np
import os

def readp2m(resultsPath, freqDir, caseDir, ioCase, hcCase, cols, rows):
    
    filesList = list(set(os.listdir(resultsPath + ioCase + freqDir + hcCase + caseDir)) - {'desktop.ini'})

    if rows > 1:
        signalData = np.empty((cols, rows))
    else:
        signalData = np.empty(cols)

    i = 0
    
    for fileName in filesList:
        path = resultsPath + ioCase + freqDir + hcCase + caseDir + fileName
        print(path)
        data = genfromtxt(path, delimiter=' ')
        if data.ndim > 1:
            signalData[i, :] = data[:, 5]
        else:
            signalData[i] = data[5]
        i += 1
    return np.array(signalData)
