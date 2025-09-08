class Packet:
        def __init__(self, command, data=None ):
            self.data = data
            self.command = command