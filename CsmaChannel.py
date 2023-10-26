from CsmaDevice import CsmaDevice
from Channel import Channel
import numpy as np

class CsmaChannel(Channel):
    def __init__(self, deviceCount, pGeneratePackage, pSendPackage, miniSlotSize):
        
        super().__init__(deviceCount, pGeneratePackage)
        self.miniSlotSize = miniSlotSize
        for i in range(1,deviceCount + 1):
            #print(f"New device, id: {i}")
            self.devices.append(CsmaDevice(i, self, pGeneratePackage/miniSlotSize, pSendPackage/miniSlotSize))

    def oneCycle(self, time):

         # Run the device once
        for i in self.devices:
            i.tick(time)
        
        # Refresh the list of active devices
        self.getActive()
        #print(self.active)

        # Refresh the list of receiver's sources
        secondaryDevices = self.getSources()
        #(self.source)
        #print('second', secondaryDevices)
        
        # Find the destinations that are not able to receive as they are sending
        destinationSending = self.getReceiverActivity()
        # Find the devices that are sending to such a destination
        deviceIdsFailinToTransmit = self.source[destinationSending] # or sending device not listed in sources

        # Find the signal and noise levels for the users
        receivedSignalMilliWatts, receivedNoiseMilliWatts = self.getNoiseAndSignalMilliWatts(self.signalStrengthMilliWatts)
        
        #print(destinationSending)
        #print(self.source)
        #print(deviceIdsFailinToTransmit)
        #print(receivedNoiseMilliWatts, receivedSignalMilliWatts)

        # Calculate the SINR based on the signal and noise levels
        sinr = np.multiply(10, np.log10(np.divide(receivedSignalMilliWatts, receivedNoiseMilliWatts)))
        
        # Find the devices that are not able to receive due to bad SINR
        exceedingSINR = sinr < 18 # VARIABLE
        #print(exceedingSINR)
        
        # Check which transmissions are successful device by device
        for i in range(0, self.deviceCount):

            # A collision is appened if one of the following conditions are true
            # (1) Device is active and the destination of the sender is in the list of devices that cannot receive due to a bad SINR
            # (2) Device has been sending to a transmitting device
            # (3) Device has been sending to a device that is receiving another transmission that is stronger
            # (4) Device is still sending a packet that has already collided
            if (self.active[i] and exceedingSINR[self.devices[i].destinationId - 1]) or (i + 1) in deviceIdsFailinToTransmit or self.devices[i].collisionOccured or secondaryDevices[i]:
                self.devices[i].collision() # Tell the device that the transmission has been unsuccessful
                self.packages += 1          # Count as a sent mini slot

            # Transmission is successful if the device is active, the last mini slot of the packet has been sent and the device is not in timeout
            elif self.active[i] and self.devices[i].remainingToSend == 0 and not bool(self.devices[i].timeOut):
                #self.devices[i].reset()
                self.packages += 1                      # Count as a sent mini slot
                self.successful += self.miniSlotSize    # Count time equal to mini slot size as successful
            
            # Explain this
            elif self.active[i] and not self.devices[i].collisionOccured and not bool(self.devices[i].timeOut):
                self.packages += 1

        # Record the activity of this round
        self.history.append(self.active.astype(int))

    # Run the channel for n times
    def runCycle(self, n = 1):
        for i in range(0, n):
            self.oneCycle(i)