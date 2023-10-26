from Device import Device
import random
import numpy as np

class CsmaDevice(Device):
    def __init__(self, i, channel, pGeneratePackage, pSendPackage):
        super().__init__(i, channel, pGeneratePackage)
        self.pSendPackage = pSendPackage
        self.timeOut = 0
        self.lastRoundNoise = 0
        self.remainingToSend = 0
        self.collisionOccured = False
        self.collisionCount = 0

    # Finds the noise in the channel and assigns it to a variable. This is used to identify if we see the channel occupied.
    def getLastRoundNoise(self):
        self.lastRoundNoise = sum(np.multiply(self.channel.active, self.channel.signalStrengthMilliWatts[:, self.id - 1]))
        #print(self.channel.active.astype(int), self.channel.source, self.lastRoundNoise)

    # Sets the device to idle mode, resetting the destination and sending status
    def reset(self, currentTime):
        self.sending = False
        self.destinationId = None
        self.collisionOccured = False
        self.collisionCount = 0
        self.channel.delay.append(currentTime - self.sendingTime - self.channel.miniSlotSize)
        self.sendingTime = 0

    # Simulates the situation when a collision has occured
    def collision(self):
        self.collisionOccured = True    # To define that during this attempt a collision has occured

        # If a collision has occured and the device has finished sending of the packet, set a timeout after which a resending can be attempted.
        if not bool(self.remainingToSend) and not bool(self.timeOut):
            
            self.collisionCount += 1                                    # Count as a collision
            self.timeOut = random.randint(2, 2 ** self.collisionCount)  # Choose a random timeout
            self.collisionOccured = False                               # Finish the handling of the collision

    # Simulate the one time slot behaviour of the device
    def tick(self, currentTime):
        #print(self.channel.occupiedChannelTreshold, self.lastRoundNoise)
        
        # Run this if the device is in a timeout
        if bool(self.timeOut):  # IS THIS CORRECT?? Should it be timeout OR collisionoccured ??
            #print(self.id, 'timeout', self.timeOut)
            #print(self.id, 'remaining', self.remainingToSend, 'delayed', self.delayed, 'sending', self.sending, 'dest', self.destinationId)
            #print(self.lastRoundNoise)
            
            # If the device has something left to send, reduce it by one
            if bool(self.remainingToSend):
                self.remainingToSend -= 1
                return
            
            # If there is not anything to send, reduce timeout by one and set device as delayed (Delayed = will not be identified as active)
            else:
                self.timeOut -= 1
                self.delayed = True
                return

        # When the device is delayed
        if self.delayed:

            # Channel and the resending probability will be checked for a new attempt. Else nothing will happend and the device will wait the next round.
            if self.lastRoundNoise < self.channel.occupiedChannelTreshold and random.random() < self.pSendPackage:
                self.remainingToSend = self.channel.miniSlotSize    # Set the packet length to identify what is left to send
                self.delayed = False                                # Not delayed anymore
        
        # If the device is not having a delay
        if not self.delayed:

            # If something is left, reduce by one
            if bool(self.remainingToSend):
                self.remainingToSend -= 1

            # Device past a successful transmission:
            # If there is nothing to send but the sending variable is true and the device is not handling a collision, reset the device.
            elif self.sending and not self.collisionOccured:
                #print('reset')
                self.reset(currentTime)
            
            # If the device is not sending and the generation of a packet happens
            if not self.sending and random.random() < self.pGeneratePackage:
                self.sendingTime = currentTime
                self.sending = True             # Set the status of the device to having something to send
                self.findReachableDevices()     # Refresh the possible destinations (THIS COULD BE MOVED??)
                self.remainingToSend = self.channel.miniSlotSize - 1                        # Set the remaining sending time
                self.delayed = self.lastRoundNoise > self.channel.occupiedChannelTreshold   # If the channel is too noisy, delay the sending
                self.destinationId = (random.choice(self.listOfDestinations) + 1)           # Choose a random destination
                
                # DEBUGGING
                #if self.id == 3:
                #    self.destinationId = (random.choice(self.listOfDestinations) + 1)
                #else:
                #    self.destinationId = 3
                #print('Current destination:', self.destinationId)
#        if self.sending and not self.delayed and not self.collisionOccured:
#            print('sending')

        # Refresh the channel noise of the previous round
        self.getLastRoundNoise()    # TODO Where to place this?? <-RELEVANT!! To the channel in a foreach system maybe?
        
        #print(self.id, 'remaining', self.remainingToSend, 'delayed', self.delayed, 'sending', self.sending, 'dest', self.destinationId)
