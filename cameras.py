import serial
from wtforms import BooleanField, IntegerField, FloatField, StringField, SelectField, FormField
from wtforms.fields.html5 import DecimalRangeField, IntegerRangeField
from wtforms import validators
from wtforms import Form
from forms import ToggleField, IntegerRangeWithNumberField

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



class IMIWhiteBalanceForm(Form):
    white_balance_mode = SelectField(
        "Mode",
        choices=[(0, 'ATW'), (1, 'AWC'), (2, 'INDOOR'), (3, 'OUTDOOR'), (4, 'MANUAL'), (5, 'AWB')]
    )
    manual_blue_gain = IntegerRangeWithNumberField(
        "Blue Gain",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=1, max=100, message='min:%(min)s max%(max)s')
        ],
        default=100
    )
    manual_red_gain = IntegerRangeWithNumberField(
       "Red Gain",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=1, max=100, message='min:%(min)s max%(max)s')
        ],
        default=100
    )
    awc_set = ToggleField('AWC Set')


class IMIHueForm(Form):
    hue_gain_r = IntegerRangeWithNumberField(
        "Red",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=0, max=255, message='min:%(min)s max%(max)s')
        ],
        default=255,
        minimum=1,
        maximum=255,
    )

    hue_gain_g = IntegerRangeWithNumberField(
        "Green",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=0, max=255, message='min:%(min)s max%(max)s')
        ],
        default=255,
        minimum=1,
        maximum=255,
    )

    hue_gain_b = IntegerRangeWithNumberField(
        "Blue",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=0, max=255, message='min:%(min)s max%(max)s')
        ],
        default=255,
        minimum=1,
        maximum=255,
    )


class IMIRegistersForm(Form):
    white_balance = FormField(IMIWhiteBalanceForm, label="White Balance")
    hue = FormField(IMIHueForm, label='Hue')


class IMIRemote(Form):
    camera_id = SelectField(
        "Camera ID",
        choices=[(c, c) for c in ['all', 1, 2, 3, 4, 5, 6]]
    )
    port = SelectField(
        "Port",
        choices=[('usb0', 'usb0')]
    )


class IMIRemoteForm(Form):
    config = FormField(IMIRemote, label='Selection')


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
        registers=IMIRegistersForm(),
        remote=IMIRemoteForm()
    )



    # pages = dict(
    #     remote=OrderedDict(
    #         port=SelectField("port", [('usb0', 'usb0')])
    #     ),
    #     registers=OrderedDict(
    # )
    # )



    @property
    def commands(self):
        return dict([(key, '#OKC=%s\r' % value) for key, value in self._commands.iteritems()] )


class CISCamera(Camera):
    pass
