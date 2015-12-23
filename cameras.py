import serial
from collections import OrderedDict
from wtforms import BooleanField, IntegerField, FloatField, StringField, SelectField
from wtforms import validators
from wtforms.fields.html5 import DecimalRangeField, IntegerRangeField

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
    # _commands = dict(
    #     up='01',
    #     down='02',
    #     left='03',
    #     right='04',
    #     enter='00',
    #     # wb = dict(
    #     #     values= []
    #     #         atw=5
    #     # )
    # )
    # port = '/dev/ttyUSB0'

    pages = dict(
        remote=OrderedDict(
            camera_id=SelectField(
                    "Camera ID",
                    choices=[(c, c) for c in ['all', 1, 2, 3, 4, 5, 6]]
            ),
            port=SelectField("port", [('usb0', 'usb0')])
        ),
        registers=OrderedDict(
            white_balance_mode=SelectField(
                "White Balance Mode",
                choices=[(0, 'ATW'), (1, 'AWC'), (2, 'INDOOR'), (3, 'OUTDOOR'), (4, 'MANUAL'), (5, 'AWB')]
            ),
            manual_blue_gain=IntegerField(
                label="Blue Gain",
            ),
            manual_red_gain=IntegerRangeField(
                label="Red Gain",
                validators=[
                    validators.Required(),
                    validators.NumberRange(min=1, max=100, message='no no no!')
                ],
                default=100
            ),
            percent=BooleanField(label='Percent')
        )
    )



    @property
    def commands(self):
        return dict([(key, '#OKC=%s\r' % value) for key, value in self._commands.iteritems()] )


class CISCamera(Camera):
    pass
