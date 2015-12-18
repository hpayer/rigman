import serial


class Camera(object):

    @property
    def port(self):
        raise NotImplemented('not impllemented')

    def execute(self, command, camera_id='all'):
        ser = serial.Serial(self.port)
        result = ser.write(self.commands[command])
        ser.close()


class IMICamera(Camera):
    _commands = dict(
        up='01',
        down='02',
        left='03',
        right='04',
        enter='00',
    )
    port = '/dev/ttyUSB0'

    @property
    def commands(self):
        return dict([(key, '#OKC=%s\r' % value) for key, value in self._commands.iteritems()] )


class CISCamera(Camera):
    pass
