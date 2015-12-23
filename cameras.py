import serial


class Parameter(object):
    def __init__(self, label, default_value):
        self.label = label
        self.default = default_value
        self.value = None


class boolParameter(object):
    def __init__(self, label, default_value):
        self.label = label
        self.default = default_value
        self.value = None


class IntParameter(Parameter):
    def __init__(self, label, default_value, min=0, max=100):
        super(IntParameter, self).__init__(label, default_value)
        self.min = min
        self.max = max


class FloatParameter(Parameter):
    def __init__(self, label, default_value, min=0, max=100):
        super(Float, self).__init__(label, default_value)
        self.min = min
        self.max = max
        
class Camera(object):

    @property
    def port(self):
        raise NotImplemented('not impllemented')

    # def execute(self, command, camera_id='all'):
    #     ser = serial.Serial(self.port)
    #     result = ser.write(self.commands[command])
    #     ser.close()

    def execute(self, command, camera_id='all'):
        print command, camera_id


class IMICamera(Camera):
    _commands = dict(
        up='01',
        down='02',
        left='03',
        right='04',
        enter='00',
        # wb = dict(
        #     values= []
        #         atw=5
        # )
    )
    port = '/dev/ttyUSB0'



    @property
    def commands(self):
        return dict([(key, '#OKC=%s\r' % value) for key, value in self._commands.iteritems()] )


class CISCamera(Camera):
    pass
