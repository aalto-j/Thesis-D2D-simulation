import numpy as np
from dbConversion import *

class Channel:
    
    def __init__(self, deviceCount, generateProbability):
        self.deviceCount = deviceCount                              # Number of devices
        self.devices = []                                           # List of device instances
        self.signalStrengthMilliWatts = 0                           # List of signal strength reveived from another UE
        self.interferenceSignalStrengthMilliWatts = np.zeros((3, deviceCount))     # List of interfering signal strength at the basestation
        self.generateProbability = generateProbability              # Probability to generate a packet
        self.packages = 0                                           # Count of sending attempts
        self.successful = 0                                         # Count of successful packets transmitted
        self.active = np.zeros(deviceCount)                         # List of currently active device
        self.source = np.zeros(self.deviceCount, dtype=int)         # List of the transmitters the users are receiving from
        self.history = []                                           # Active device history size (Devices, Time)
        self.occupiedChannelTreshold = 1e-6                         # Limit for devices to identify CSMA channel as occupied
        self.miniSlotSize = 1                                       # Packet length (mini slot size), relevant for CSMA, 1 for Aloha
        self.delay = []

    def __str__(self):
        return f"Channel, {self.deviceCount} devices, p = {self.generateProbability}"

        # Assign signal strength values to this channel
    def setSignalStrengthMilliWatts(self, signalStrengthMilliWatts):
        np.fill_diagonal(signalStrengthMilliWatts, 0)
        self.signalStrengthMilliWatts = signalStrengthMilliWatts

        # Assign interfering signal strength values to this channel
    def setInterferenceSignalStrengthMilliWatts(self, interferenceSignalStrengthMilliWatts):
        self.interferenceSignalStrengthMilliWatts = interferenceSignalStrengthMilliWatts

        # (1) Returns the signal level for each device
        # (2) Returns ths interference each device will be receiving the active devices except the one it is receiving from
    def getNoiseAndSignalMilliWatts(self, _):
        #receivedNoiseMilliWatts = np.zeros(self.deviceCount)
        receivedNoiseMilliWatts = np.multiply(np.ones(self.deviceCount), dbm2mw(np.array([-114])))  # Setting the background noise
        receivedSignalMilliWatts = np.zeros(self.deviceCount)
        for i in range(0, self.deviceCount):

            if self.source[i] != 0:

                #receivedNoiseMilliWatts = np.zeros(self.deviceCount)#
                receivedSignalMilliWatts[i] = self.signalStrengthMilliWatts[self.source[i] - 1, i]
                #print(activeCopy, self.signalStrengthMilliWatts[:, i])
                activeTemp = self.active.copy()
                activeTemp[self.source[i] - 1] = 0
                #print(activeTemp)
                receivedNoiseMilliWatts[i] = sum(np.multiply(activeTemp, self.signalStrengthMilliWatts[:, i]))
        return receivedSignalMilliWatts, receivedNoiseMilliWatts

        # Assigns the list of active devices to a variable
    def getActive(self):
        self.active = np.multiply([d.sending for d in self.devices], [not d.delayed for d in self.devices])

        # Assigns the sources list of receiving devices to a variable and returns a list of devices that sent to a device that receives something else
    def getSources(self):
        
        self.source = np.zeros(self.deviceCount, dtype=int)
        secondaryDevices = [False]*self.deviceCount
        for i in range(0, self.deviceCount):
            if self.active[i]:
                destinationIdx = self.devices[i].destinationId - 1
                if self.source[destinationIdx] == 0:
                    self.source[destinationIdx] = self.devices[i].id
                elif self.signalStrengthMilliWatts[i, destinationIdx ] > self.signalStrengthMilliWatts[self.source[destinationIdx] - 1, destinationIdx]:
                    secondaryDevices[self.source[destinationIdx] - 1] = True
                    self.source[destinationIdx] = self.devices[i].id
                else:
                    secondaryDevices[i] = True
        return secondaryDevices

        # Prints the history, mainly for debugging purpose
    def printHistory(self):
        for round in self.history:
            print(np.array2string(round, separator='\t'))
        print(self.successful, '/', self.packages)

        # Returns a list of device ids that will be receive a certain signal level
    def getSignalStrengthDestinationsMilliWattsByID(self, id):
        return np.argwhere(self.signalStrengthMilliWatts[id - 1, :] > dbm2mw(np.array([-90]))).flatten() # VARIABLE

        # Returns the devices instance based on the id
    def getDeviceById(self, id):
        return self.devices[id - 1]

        # Returns true if the receiver is sending
    def getReceiverActivity(self):
        return np.multiply(self.active, [d > 0 for d in self.source])

        # Returns values and lists that will contain information about the interference at the base station
    def getInterference(self, bsNumber, time):
        #print(self.interferenceSignalStrengthMilliWatts[0][1])
        interferenceDeviceXTick = np.multiply([self.interferenceSignalStrengthMilliWatts[0][bsNumber]] * time, self.history)
        interferenceTick = []
        for i in interferenceDeviceXTick:
            interferenceTick.append(sum(i))
        quantile90 = np.quantile(interferenceTick, 0.9)
        quantile95 = np.quantile(interferenceTick, 0.95)
        maximum = np.max(interferenceTick)

        timeAtQuantile90 = sum(1 for i in interferenceTick if i >= quantile90) / len(interferenceTick)
        timeAtQuantile95 = sum(1 for i in interferenceTick if i >= quantile95) / len(interferenceTick)
        timeAtMax = sum(1 for i in interferenceTick if i == maximum) / len(self.history)
        #print(timeAtMax)
        #print(interferenceTick)
        return np.mean(interferenceTick), maximum, quantile90, timeAtQuantile90, timeAtQuantile95, timeAtMax
