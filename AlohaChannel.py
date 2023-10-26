from AlohaDevice import AlohaDevice
from Channel import Channel
import numpy as np

class AlohaChannel(Channel):
    def __init__(self, deviceCount, pGeneratePackage):
        
        super().__init__(deviceCount, pGeneratePackage)
        self.miniSlotSize = 1   # THe mini slot size with aloha is always 1
        for i in range(1,deviceCount + 1):
            #print(f"New device, id: {i}")
            self.devices.append(AlohaDevice(i, self, pGeneratePackage))
        
        
        

    def __str__(self):
        return f"Aloha channel, device count {self.deviceCount}, p = {self.generateProbability}"
    
    def oneCycle(self, time):
        #print('alohacycle')
        
        # Run the device once
        for i in self.devices:
            i.tick(time)

        # Refresh the list of active devices
        self.getActive()
        
        # Refresh the list of receiver's sources
        secondaryDevices = self.getSources()
        
        # Find the destinations that are not able to receive as they are sending
        destinationSending = self.getReceiverActivity()
        # Find the devices that are sending to such a destination
        deviceIdsFailinToTransmit = self.source[destinationSending]

        # Find the signal and noise levels for the users
        receivedSignalMilliWatts, receivedNoiseMilliWatts = self.getNoiseAndSignalMilliWatts(self.signalStrengthMilliWatts)
        # For debugging
        # print(receivedNoiseMilliWatts, receivedSignalMilliWatts)

        # Calculate the SINR based on the signal and noise levels
        sinr = np.multiply(10, np.log10(np.divide(receivedSignalMilliWatts, receivedNoiseMilliWatts)))
        
        # Find the devices that are not able to receive due to bad SINR
        exceedingSINR = sinr < 18 # VARIABLE
        #print(exceedingSINR)
        #jokuarray = []
        # Check which transmissions are successful device by device
        for i in range(0, self.deviceCount):

            # BUG Aloha not going todelayed

            # A collision is appened if one of the following conditions are true
            # (1) Device is active and the destination of the sender is in the list of devices that cannot receive due to a bad SINR
            # (2) Device has been sending to a transmitting device
            # (3) Device has been sending to a device that is receiving another transmission that is stronger
            if (self.active[i] and exceedingSINR[self.devices[i].destinationId - 1]) or (i + 1) in deviceIdsFailinToTransmit or secondaryDevices[i]:
                #jokuarray.append('c')
                
                self.devices[i].collision() # Tell the device that the transmission has been unsuccessful
                self.packages += 1          # Count as a sent packet
            
            # Transmission is successful if the device is active and none of the previous conditions have been fulfilled
            elif self.active[i]:
                #jokuarray.append('s')
                self.devices[i].reset(time)                     # Set the device to the idle mode
                self.packages += (1 * self.miniSlotSize)    # Count as a sent packet
                self.successful += (1 * self.miniSlotSize)  # Count as a successfully sent packet
                #else:jokuarray.append('i')
        #print(jokuarray)
        # Record the activity of this round
        self.history.append(self.active.astype(int))
    
    # Run the channel for n times
    def runCycle(self, n = 1):
        for i in range(0, n):
            self.oneCycle(i)

    