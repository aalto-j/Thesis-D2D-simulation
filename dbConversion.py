from math import log10
import numpy as np

def dbm2mw(dataIn):
    
    a = lambda t: 1*10**(t/10)
    dataOut = np.empty_like(dataIn)
    
    for idx, x in np.ndenumerate(dataIn):
        dataOut[idx] = a(x)
    return dataOut

def mw2dbm(dataIn: list):
    
    dataOut = []
    
    for i in dataIn:
        if i == 0.0:
            dataOut.append(float('-inf'))
        else:
            dataOut.append(10*log10(i))
    return dataOut