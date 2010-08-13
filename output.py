import alsaaudio


class Output(object):
    output = None

    def write(self, data):
        self.output.write(data)


class AlsaOutput(Output):
    def __init__(self):
        self.output = alsaaudio.PCM()