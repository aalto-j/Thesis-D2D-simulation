class Device:

    def __init__(self, id, channel, pGeneratePackage):
        self.id = id
        self.sending = False
        self.delayed = False
        self.pGeneratePackage = pGeneratePackage
        self.listOfDestinations = None
        self.destinationId = None
        self.channel = channel
        self.sendingTime = 0                                # Variable to record the sending time, needed to find the delay

        # Sets the variable of possible destinations
    def findReachableDevices(self):
        self.listOfDestinations = self.channel.getSignalStrengthDestinationsMilliWattsByID(self.id).tolist()
        #print('Available:', self.listOfDestinations)