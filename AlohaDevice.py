from Device import Device 
import random

class AlohaDevice(Device):
    
    def __str__(self) -> str:
        return f"Aloha device, id {self.id}"
    
    # Simulate the one time slot behaviour of the device
    def tick(self, currentTime):
        if not self.sending and not self.delayed and random.random() < self.pGeneratePackage:
            self.sendingTime = currentTime
            self.sending = True
            self.findReachableDevices() # Can this be moved?
            self.destinationId = random.choice(self.listOfDestinations) + 1
            #print("yes")
        elif self.delayed and random.random() < self.pGeneratePackage:
            self.delayed = False

    # Simulates the situation when a collision has occured
    def collision(self):
        self.delayed = True

    # Sets the device back to idle mode, resets destination
    def reset(self, currentTime):
        #print(currentTime - self.sendingTime - self.channel.miniSlotSize + 1)
        self.channel.delay.append(currentTime - self.sendingTime - self.channel.miniSlotSize + 1)
        self.sendingTime = 0
        self.sending = False
        self.destinationId = None