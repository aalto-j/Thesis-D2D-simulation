from AlohaChannel import AlohaChannel
from CsmaChannel import CsmaChannel
import numpy as np
from readP2m import readp2m
from dbConversion import *
import csv


def simulate(resultsPath, freqChoise, indoor_bool, harbour_bool, basestation, dev, power, alohaMode):

    listOfFreq = ['700M/', '3.5G/', '6G/', '26G/', '60G/', '100G/']
    listOfBS = ['BS1/', 'BS2/', 'BS3/']
    
    listOfFreqHz = [7e8, 35e8, 6e9, 26e9, 60e9, 10e10]

    freqDir = listOfFreq[freqChoise]
    
    caseDir = 'UE/'
    rfiDir = listOfBS[basestation]
    
    if indoor_bool:
        ioCase = 'Indoor/'
    else:
        ioCase = 'Outdoor/'
    
    if harbour_bool:
        hcCase = 'Harbour/'
    else:
        hcCase = 'City/'
    
    figDir = 'h10i/'

    pStep = 0.01
    pRange = np.arange(0 + pStep, 1- pStep, pStep)

    totalTransmittedPackets         = np.zeros((len(listOfBS), len(pRange)))
    successfullyTransmittedPackets  = np.zeros((len(listOfBS), len(pRange)))
    interferencePowerMeanLst        = np.zeros((len(listOfBS), len(pRange)))
    interferencePowerMaximumLst     = np.zeros((len(listOfBS), len(pRange)))
    interferencePowerQuantileLst    = np.zeros((len(listOfBS), len(pRange)))
    timeAtQuantile90                = np.zeros((len(listOfBS), len(pRange)))
    timeAtQuantile95                = np.zeros((len(listOfBS), len(pRange)))
    timeAtMaximum                   = np.zeros((len(listOfBS), len(pRange)))
    delayLst                        = np.zeros((len(listOfBS), len(pRange)))

    miniSlotSize = 1 if alohaMode else 100
    time = 1000
  
    signalPower             = dbm2mw(readp2m(resultsPath, freqDir, caseDir, ioCase, hcCase, dev, dev))
    
    
    interferenceSignalPower = np.zeros((3, dev), dtype=float)

    for idx, pathBS in enumerate(listOfBS):
        interferenceSignalPower[idx] = dbm2mw(readp2m(resultsPath, freqDir, pathBS, ioCase, hcCase, dev, 1))

    interferenceSignalPower = [interferenceSignalPower] * time * miniSlotSize

    #channels = np.empty((len(pRange)), dtype=CsmaChannel)
    channels = np.empty((len(pRange)), dtype=AlohaChannel)

    for i in range(0, len(pRange)):
        #channels[i] = CsmaChannel(dev, pRange[i], pRange[i], miniSlotSize)
        if alohaMode:
            channels[i] = AlohaChannel(dev, pRange[i])
        else:
            channels[i] = CsmaChannel(dev, pRange[i], 0.1, miniSlotSize)
        #print(channels[i])


    load = np.multiply(pRange, dev)
    #idx = 0

    with open('allResults10dbm.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
 
        for idx, ch in enumerate(channels):
            ch.setSignalStrengthMilliWatts(signalPower)
            ch.setInterferenceSignalStrengthMilliWatts(interferenceSignalPower) #FIX
            ch.runCycle(time*ch.miniSlotSize)

            for i in range(0,3):

                mean, max, quantile90, timeAtQ90, timeAtQ95, timeAtMax = ch.getInterference(i, time*miniSlotSize)
                interferencePowerMeanLst[i, idx] = mean
                interferencePowerMaximumLst[i, idx] = max
                interferencePowerQuantileLst[i, idx] = quantile90
                successfullyTransmittedPackets[i, idx] = ch.successful
                totalTransmittedPackets[i, idx] = ch.packages
                timeAtQuantile90[i, idx] = timeAtQ90
                timeAtQuantile95[i, idx] = timeAtQ95
                timeAtMaximum[i, idx] = timeAtMax
                delayLst[i, idx] = np.mean(ch.delay)
            
                writer.writerow([listOfFreqHz[freqChoise], indoor_bool, harbour_bool, i, load[idx], dev, power, interferencePowerMaximumLst[i, idx], interferencePowerQuantileLst[i, idx], interferencePowerMeanLst[i, idx], np.divide(successfullyTransmittedPackets[i, idx], time*miniSlotSize), delayLst[i, idx], timeAtQ90, timeAtQ95, timeAtMax, 'A' if alohaMode else 'C'])

    return
    

def main():

    fields = ['f', 'indoor_ue', 'harbour_bool', 'basestation', 'load', 'n', 'power', 'RFI_max', 'RFI_Q90', 'RFI_mean', 'throughput', 'delay', 'time_Q90', 'time_Q95', 'time_max', 'ch']
    with open('allResults10dbm.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        csvfile.close()

    #resultsPath = './Simulation-10dbm results/'
    resultsPath = './Simulation-23dbm results/'
    #results50Path = './Simulation-23dbm50 results/'
    for monteCarlo_run in range(0, 5):
        print(monteCarlo_run)
        for frequencyChoise in [2]:#range(0, 6):
            for indoor in [True]:#[True, False]:
                for harbour in [True]:
                   #for bs in range(0, 3): #Not needed
                    simulate(resultsPath, frequencyChoise, indoor, harbour, 0, 10, 23, True)
                    simulate(resultsPath, frequencyChoise, indoor, harbour, 0, 10, 23, False)
                
main()